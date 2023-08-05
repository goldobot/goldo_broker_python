The implementation of asynchronous commands is done using asyncio futures.

the synopsis for a nucleo command is as follow:
a command is implemented as a function that:
assign a sequence number to the command.
create an asyncio future object and store it in a dict, referenced by the sequence number.

use add_done_callback to remove the future from the dict when it is resolved, using code similar to this:
future.add_done_callback(functools.partial(self._remove_future, sequence_number))

send the command message, including sequence number, to the nucleo
await the future

The module implementing the command should register a callback for reacting to the ack or command finish message from the nucleo.
On response, retrieve the corresponding future using the sequence number from the message and call set_result on it to resolve it.
this will unblock the task that is awaiting the future.
you can call set_exception on the future to trigger an exception in case of error.


