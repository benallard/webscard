scard = require("scard")

function apdutostring(apdu)
   function hex(int)
      return string.format("%02X", int)
   end
   t2 = {}
   for k, v in pairs(apdu) do
      table.insert(t2, hex(v))
   end
   return table.concat(t2, " ")
end


hresult, hcontext = scard.establishcontext(0)
print ("EstablishContext: "..hresult)
hresult, readers = scard.listreaders(hcontext, {})
print ("ListReaders: "..hresult)
if #readers ~= 0 then
   print (readers[1])
   hresult, hcard, protocol = scard.connect(hcontext, readers[1], 2 ,3)
   hresult, answer = scard.transmit(hcard, protocol, {0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00})
   print ("Received: "..apdutostring(answer))
   hresult, answer = scard.transmit(hcard, protocol, {0x80, 0xCA, 0x9F, 0x7F, 0x00})
   print ("Received: "..apdutostring(answer))
   hresult = scard.disconnect(hcard, 0)
end
hresult = scard.releasecontext(hcontext)