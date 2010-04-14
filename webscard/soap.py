from webscard.implementations.chooser import createimpl, instanciateimpl

from werkzeug import Response

from elementtree.ElementTree import Element, SubElement, ElementTree

def shouldexit(hresult, opelem):
    return (hresult != 0) and not bool(opelem.get("ignorefailure", "0"))

def v1(request):
    root = request.xmlroot
    if root is None:
        return Response("No body")
    implname = root.get("implementation", "pyscard")

    impldict = createimpl(implname)
    impl = instanciateimpl(impldict, request.session)

    res = Element('root')

    context = None
    card = None
    activeprot = None

    for opelem in root.findall('operation'):
        name = opelem.get('name')
        if name not in ['establishcontext', 'connect', 'transmit',
                        'disconnect','releasecontext']:
            SubElement(res, name).text = "Operation not recognized"
            continue
        if name == 'establishcontext':
            op = impl.SCardEstablishContext
            dwScope = int(opelem.get('dwScope', "2"))
            hresult, context = op(dwScope)
            SubElement(res, name, hresult=str(hresult), context=str(context))
            if shouldexit(hresult, opelem):
                break
        elif name == 'connect':
            op = impl.SCardConnect
            readername=opelem.get("readername")
            if context is None:
                SubElement(res, name).text = "No context"
                continue
            if readername is None:
                SubElement(res, name).text = "No ReaderName specified"
                continue
            shared = int(opelem.get("dwShared", "2"))
            prot = int(opelem.get("dwPreferredProtocol", 3))
            hresult, card, activeprot = op(context, readername, shared, prot)
            SubElement(res, name, hresult=str(hresult), card=str(card), activeprot=str(activeprot))
            if shouldexit(hresult, opelem):
                break
        elif name == 'transmit':
            op = impl.SCardTransmit
            prot = int(opelem.get("dwProtocol", str(activeprot)))
            apdu = []
            for node in opelem:
                if node.tag == 'cmd':
                    byte = int(node.text)
                    if byte > 0 and byte < 0x100:
                        apdu.append(byte)
            hresult, response = op(card, prot, apdu)
            cur = SubElement(res, name, hresult=str(hresult))
            for byte in response:
                SubElement(cur, "cmd").text = str(byte)
            if shouldexit(hresult, opelem):
                break
        elif name == 'disconnect':
            op = impl.SCardDisconnect
            disp = int(opelem.get("dwDisposition", "0"))
            hresult = op(card, disp)
            SubElement(res, name, hresult=str(hresult))
            if shouldexit(hresult, opelem):
                break
        elif name == 'releasecontext':
            op = impl.SCardReleaseContext
            hresult = op(context)
            SubElement(res, name, hresult=str(hresult))
            if shouldexit(hresult, opelem):
                break

    impldict['release'](request.session)

    f = FileObj()
    ElementTree(res).write(f)

    return Response(f.data, content_type="application/json+xml")

class FileObj(object):
    data = ""
    def write(self, data):
        self.data += data
