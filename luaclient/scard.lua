local json = require ("json")
local curl = require ("curl")
local string = require("string")

local assert = assert
local print = print

module("scard")

local answer

local server = [[http://10.0.6.111:3333/]]

local function receive(s,b)
   -- stores the received data in the table t
   answer = b
   -- return number_of_byte_served, error_message
   -- number_of_byte_served ~= len is an error
   return string.len(b)
end

local c = assert(curl.new())
assert(c:setopt(curl.OPT_WRITEFUNCTION,receive))
assert(c:setopt(curl.OPT_HTTPHEADER, "Indent: no"))


function establishcontext(scope)
   assert(c:setopt(curl.OPT_URL, server.."EstablishContext/"..scope))
   assert(c:perform())
   local o = json.decode(answer)
   return o.hresult, o.hcontext
end

function releasecontext(hcontext)
   assert(c:setopt(curl.OPT_URL, server..hcontext.."/ReleaseContext"))
   assert(c:perform())
   local o = json.decode(answer)
   return o.hresult
end

function listreaders(hcontext, group)
   group = json.encode(group)
   assert(c:setopt(curl.OPT_URL, server..hcontext.."/ListReaders/"..group))
   assert(c:perform())
   local o = json.decode(answer)
   return o.hresult, o.readers
end

function connect(hcontext, reader, shared, protocol)
   reader = curl.escape(reader)
   assert(c:setopt(curl.OPT_URL, server..hcontext.."/Connect/"..reader.."/"..shared.."/"..protocol))
   assert(c:perform())
   local o = json.decode(answer)
   return o.hresult, o.hCard, o.dwActiveProtocol
end

function disconnect(hcard, disposition)
   assert(c:setopt(curl.OPT_URL, server..hcard.."/Disconnect/"..disposition))
   assert(c:perform())
   local o = json.decode(answer)
   return o.hresult
end

function transmit(hcard, protocol, apdu)
   apdu = json.encode(apdu)
   apdu = curl.escape(apdu)
   assert(c:setopt(curl.OPT_URL, server..hcard.."/Transmit/"..protocol.."/"..apdu))
   assert(c:perform())
   local o = json.decode(answer)
   return o.hresult, o.response
end