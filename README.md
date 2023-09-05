# Remote Phone Control - v0.1.0

Some SIP hardphone brands support the features _Action URIs_ and _Action URLs_ on some or all of their phone models. _Action URIs_ are used to _remote control_ a phone by sending it _HTTP GET_ requests. E.g., place a call. _Action URLs_ are used to _communicate events_ occuring on a phone to an _HTTP service_. E.g. an incoming call.

> This Python package primarily serves as a _remote controller_ and a _listener_ for the _**call related**_ _commands to_ and _events from_ a phone. Its main intent and focus is _to automate the testing of call scenarios_.

## Supported phones

In principle, _Remote Phone Control_, could be extended to support any phone that provides the _Action URI_ and _Action URL_ features. Currently, only the SNOM models noted under the _Stack_ heading are tested and supported.

## Action URIs and methods

These are _HTTP GET_ requests with _query parameters_ to control a phone, make it do something. _remote_phone_control_ hides the URIs and query parameters in a phone class object, e.g. `Snom`, and its methods. The _methods_ are mapped to and use _corresponding URI and query parameters_. The table below lists currently implemented methods for `Snom` class objects. The method names are quite self explanatory. A description is provided if more clarification is needed. Consult [SNOM Remote phone control via http](https://service.snom.com/display/wiki/Remote+phone+control#Remotephonecontrol-ViaHTTP) for reference.

Method | Arguments | Returns | Description
---------|----------|---------|---------
 callout | number: str | bool |
 pickup | None | bool |
 hangup | None | bool |
 hangup_onhook | None | bool |
 hangup_all | None | bool |
 senddtmf | digits: str | bool | Send in-band DTMF
 senddtmf_sipinfo | digits: str | bool | Send DTMF using SIP-INFO
 expect | event: Literal['incoming', 'connect', 'disconnect'], timeout: int = event_wait_timeout| bool | Returns `True` if your expectation was correct. The default timeout to wait for the event is 15 seconds
 clear_events | None | None | Call this together with `hangup_all` in case a test goes awry and phones are left with dangling, standing calls.
 set_disable_speaker | value: Literal['on', 'off'] | bool | Turn audible cues/ the speaker on or off
 set_setting | setting: str, value: str | bool | `setting` is the name of the phone setting you want to set to `value`. For settings name reference browse to the phone's settings page: `http://<phone's ip-address>/settings.htm`
 press_px | x: str | bool | Simulates pressing a free programmable function key
 transfer | None | bool |
 reboot | None | bool |
 stop | None |  None | When you're done consuming `Snom`, you MUST call `stop` to stop the `Snom`'s _Action Server_

## Action URLs and handled events

A phone will send an _HTTP GET_ request to the _Action URL_ when triggered by an event. The _remote_phone_control_ package is the endpoint, target, of the request. It will parse and process the request.

### Event to Action URL mappings

The events currently handled by _remote_phone_control_ are per the following table.

Event | Description | Action URL used by the phone
---------|----------|----------
 Incoming call | There is an incomming call, the phone is ringing | `http://<remote_phone_control ip-address>:<port>/event?ip=$phone_ip&event=incoming&local=$local&remote=$remote`
 On Connected | Fired when a call is established | `http://<remote_phone_control ip-address>:<port>/event?ip=$phone_ip&event=connected&local=$local&remote=$remote`
 On Disconnected | A call is ended | `http://<remote_phone_control ip-address>:<port>/event?ip=$phone_ip&event=disconnected&local=$local&remote=$remote`

With _remote_phone_control_ you can use these events as verification points when testing a call. E.g., when a phone is called, we can verify if there is an incoming call. When the call is answered, we can check if there's an established call.

For further reference on _Action URL_ s consult [SNOM Action URLs](https://service.snom.com/display/wiki/Action+URLs)

### Action URL, format and query parameters

The _Action URL_ is configured on the phone. _remote_phone_control_ will configure this automatically on the phone given the ip-address of the phone. See _Usage_ for an example.

Below, the format used by _remote_phone_control_ to set the _Action URL_ on the phone.

```http
http://<Remote Phone Controller ip-address>:<port>/event?ip=$phone_ip&event=<event>&local=$local&remote=$remote
```

- `<Remote Phone Controller ip-address>`: The ip-address of the node where a _remote_phone_control_ package is run.
- `<port>`: The _Action server_ port served by _remote_phone_control_
- `$phone_ip`: A phone variable that will be replaced by the phone's ip-address
- `<event>`: indicates to _remote_phone_control_ what event triggered the request
  - Currently _remote_phone_control_ parses and handles the following `<event>`s
    - incoming
    - connected
    - disconnected
- `$local`: A phone variable that will be replaced by the local sip-id related to the event
- `$remote`: A phone variable that will be replaced by the remote sip-id related to the event

## Stack

This was used to develop and test the package. Not to say that other combinations of, e.g., Python, Ubuntu, phone models, phone firmware might also work. The SNOM models used are not very recent though. End of life even. So, no guarantees that the package will work for newer models unmodified. But my first impression after skimming through the documentation of recent SNOM models is that the _Action URI_ and _Action URL_ support looks very similar.

- Python: 3.8.10
- Ubuntu: 20.04.6 LTS
- This Python package was tested with the following SIP hardphones
  - SNOM

    Model | Firmware
    ---------|----------
    300 | 8.7.3.19, 8.7.3.25 8.7.5.17
    320 | 8.7.3.19, 8.7.3.25 8.7.5.17
    360 | 8.7.3.19, 8.7.3.25

## Installation

### From PyPI

```bash
(venv) $ pip install remote-phone-control
```

### From GibHub

```bash
(venv) $ pip install git+https://github.com/p4irin/remote_phone_control.git
```

### Verify

```bash
(venv) $ python
Python 3.8.10 (default, May 26 2023, 14:05:08) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import remote_phone_control
>>> remote_phone_control.__version__
'0.0.1'
>>> import remote_phone_control.snom
>>> dir(remote_phone_control.snom)
['ActionServer', 'Literal', 'Snom', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'requests']
>>>
```

## Usage

### Preconditions

A list of what to account for in order to remote control phones for test automation.

- Networking
  - Preferably use a setup where the node, on which _remote_phone_control_ is running, the phones, the registrar and the call proxy are on the same subnet
  - If _remote_phone_control_, the phones, the registrar and the call proxy _are_ on different subnets, make sure they can see, reach each other. E.g., look at you're routing configuration.
  - No firewall between _remote_phone_control_ and phones
  - No firewall on _remote_phone_control_ 's node, Ubuntu, as mentioned under _Stack_
  - No NAT between _remote_phone_control_ and phones
- The phones MUST be provisioned and working
  - Are registered
  - Can call each other
  - Can, optionally, call out to PSTN
  - Can, optionally, receive incoming calls originating from the PSTN
- What data you need
  - ip addresses of the phones
  - the username and password of the phones
  - allocate, list an _Action server_ port for each phone. Each phone will be controlled by a separate instance of a phone class object, e.g. `Snom`, that will also handle a phone's events through an _Action URL_
  - ip address of _remote_phone_control_ 's node. This will be used as the _Action server_'s ip-address for each phone object as you can control several phones from the same node.
  - a sip-id (outgoing URI) on the phone to use for call operations.

### Basic examples

The examples given are included in the _package_'s source as unit tests, in the _tests_ sub directory. The _package_'s tests use Python's standard library unit testing framework. For simplicity's sake, the examples below do not.

#### Imports and _Snom_ instances

These imports and _Snom_ instantiations must precede all the standalone examples.

```python
import time
from remote_phone_control.snom import Snom


snom_a = Snom(
  "nnn.nnn.nnn.nnn", # ip-address of a SNOM phone
  "nnn.nnn.nnn.nnn", # Action Server's ip-address
  nnnn, # Action Server's listening port
  "username", # username to access the SNOM
  "password", # password to access the SNOM
  "outgoing URI", # a sip-id configured on the SNOM
  "extension" # the SNOM's extension
)

snom_b = Snom(
  "nnn.nnn.nnn.nnn",
  "nnn.nnn.nnn.nnn",
  nnnn,
  "username",
  "password",
  "outgoing URI",
  "extension"
)
```

N.B.

- The _Action Server_'s ip-address is the ip-address of the node where _remote_phone_control_ is used. Remember, the _Action Server_ is served by _remote_phone_control_.
- The _Action Server_'s _listening port_ MUST be unique for each `Snom` instance
- The _outgoing URI_ is the _sip account_ used for calling

#### Example: Call out to PSTN

E.g., set your mobile phone to _auto answer_ and call it.

```python
assert snom_a.callout('PSTN number to call') == True
assert snom_a.expect('connect') == True
time.sleep(5) # Represents a 5 seconds conversation
assert snom_a.hangup() == True
assert snom_a.expect('disconnect') == True

snom_a.stop()
```

#### SNOM A calls SNOM B, B answers, call is established, B ends the call

```python
snom_a.callout("Extension of SNOM B")
assert snom_b.expect('incoming') == True
snom_b.pickup()
assert snom_b.expect('connect') == True
time.sleep(5) # Represents a 5 seconds conversation
snom_b.hangup()
assert snom_b.expect('disconnect') == True

snom_a.stop()
snom_b.stop()
```

#### A calls B, B rejects the call

```python
snom_a.callout("Extension of SNOM B")
assert snom_b.expect('incoming') == True
# Reject the incoming call
snom_b.hangup()
assert snom_a.expect('disconnect')

snom_a.stop()
snom_b.stop()
```

### An actual use case

To get a feel of how you can use this package. It proofed very useful in automating end to end regression tests of a cloud hosted call center web app where an agent is tied to a browser interface, the GUI, and a SIP phone. Call actions displayed and performed on the GUI should be in sync with the actual state of the phone and vice versa. Using Selenium, call actions are executed on the GUI and the state of the phone checked against the expectation using the package. Using the package, call actions are executed on the phone and the GUI state checked using Selenium. Inbound calls, with an external origin, i.e. PSTN, and several other scenarios are checked against both the state of the GUI and the phone. Gluing it all together with Python's standard library unittest framework.

## Reference

- SNOM
  - [Remote phone control via http](https://service.snom.com/display/wiki/Remote+phone+control#Remotephonecontrol-ViaHTTP)
  - [Action URLs](https://service.snom.com/display/wiki/Action+URLs)
  - `http://<phone's ip-address>/settings.htm`
- Yealink
  - [Action URI](https://support.yealink.com/en/portal/knowledge/show?id=03d0477da77204eb70693585)
  - [How to dial or place a call using remote control?](https://support.yealink.com/en/portal/knowledge/show?id=f8994ddaabfd7dbd59576b17)
- Python
  - [Requests: HTTP for Humans](https://requests.readthedocs.io/en/latest/)
