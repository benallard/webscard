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
   i = 0
   repeat
      i = i + 1
      print (readers[i])
      hresult, hcard, protocol = scard.connect(hcontext, readers[i], 2 ,3)
   until (hresult == 0) or (i == #readers)
   if i == #readers then
      hresult = scard.releasecontext(hcontext)
      print ("*** No SmartCard inserted")
      return
   end
   hresult, readername, state, protocol, atr = scard.status(hcard)
   print ("ATR: "..apdutostring(atr))
   hresult = scard.begintransaction(hcard)
   apdu = {0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00}
   print ("==> "..apdutostring(apdu))
   hresult, answer = scard.transmit(hcard, protocol,apdu)
   print ("<== "..apdutostring(answer))
   apdu = {0x80, 0xCA, 0x9F, 0x7F, 0x00}
   print ("==> "..apdutostring(apdu))
   hresult, answer = scard.transmit(hcard, protocol, apdu)
   print ("<== "..apdutostring(answer))
   print ("--- sent closed")
   hresult = scard.endtransaction(hcard, 0)
   print ("--- transaction closed")
   hresult = scard.disconnect(hcard, 0)
   print ("--- disconnected")
end
hresult = scard.releasecontext(hcontext)
print ("--- released")