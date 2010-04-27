from webscard.implementations.chooser import createimpl, instanciateimpl

from webscard.utils import hexlikeiwant

from werkzeug import Response

from elementtree.ElementTree import Element, SubElement, ElementTree

SUGAR = """
<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
 soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">
<soap:Body>
%s
</soap:Body>

</soap:Envelope>"""

def shouldexit(hresult, opelem):
    """ Is the error fatal """
    return (hresult != 0) or not bool(opelem.get("ignorefailure", "0"))

def version1(request):
    root = request.soapbody
    if root is None:
        return Response("No body")
    implname = root.get("implementation", "pyscard")

    impldict = createimpl(implname)
    impl = instanciateimpl(impldict, request.session)

    res = Element('operations')

    context = None
    card = None
    activeprot = None

    for opelem in root.findall('operation'):
        name = opelem.get('name')
        if name not in ['establishcontext', 'connect', 'transmit',
                        'disconnect','releasecontext']:
            SubElement(res, "operation",
                       name=name).text = "Operation not recognized"
            continue
        if name == 'establishcontext':
            op = impl.SCardEstablishContext
            dwScope = int(opelem.get('dwScope', "2"))
            hresult, context = op(dwScope)
            SubElement(res, 'operation', name=name, hresult=str(hresult),
                       context=str(context))
            if shouldexit(hresult, opelem):
                break
        elif name == 'connect':
            op = impl.SCardConnect
            readername = opelem.get("readername")
            if context is None:
                SubElement(res, 'operation', name=name).text = "No context"
                continue
            if readername is None:
                SubElement(res, 'operation',
                           name=name).text = "No ReaderName specified"
                continue
            shared = int(opelem.get("dwShared", "2"))
            prot = int(opelem.get("dwPreferredProtocol", 3))
            hresult, card, activeprot = op(context, readername, shared, prot)
            SubElement(res,'operation', name=name, hresult=str(hresult), 
                       card=str(card), activeprot=str(activeprot))
            if shouldexit(hresult, opelem):
                break
        elif name == 'transmit':
            op = impl.SCardTransmit
            prot = int(opelem.get("dwProtocol", str(activeprot)))
            apdu = []
            for node in opelem:
                if node.tag == 'byte':
                    byte = int(node.text, int(node.get('base', '10')))
                    if byte >= 0 and byte < 0x100:
                        apdu.append(byte)
            hresult, response = op(card, prot, apdu)
            cur = SubElement(res, 'operation', name=name, hresult=str(hresult))
            for byte in response:
                SubElement(cur, "byte", 
                           base="16").text = str(hexlikeiwant(byte))
            if shouldexit(hresult, opelem):
                break
        elif name == 'disconnect':
            op = impl.SCardDisconnect
            disp = int(opelem.get("dwDisposition", "0"))
            hresult = op(card, disp)
            SubElement(res, 'operation', name=name, hresult=str(hresult))
            if shouldexit(hresult, opelem):
                break
        elif name == 'releasecontext':
            op = impl.SCardReleaseContext
            hresult = op(context)
            SubElement(res, 'operation', name=name, hresult=str(hresult))
            if shouldexit(hresult, opelem):
                break

    impldict['release'](request.session)

    f = FileObj()
    ElementTree(res).write(f)
    response = SUGAR % f.data

    return Response(response, content_type="application/json+xml")

class FileObj(object):
    data = ""
    def write(self, data):
        self.data += data
