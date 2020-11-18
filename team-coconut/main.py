import re
import bots
import hata
from hata.ext.commands import CommandProcesser
from hata.ext.commands.command import COMMAND_RP

hata.start_clients()

USER_MENTION_RP = re.compile(r'<@!?(\d{7,21})>')


# this class is only if huyane doesnt add the feature to overide the checks of this class by the end of the jam
async def __call__(self, client, message):
    """
    Calls the waitfors of the command processer, processes the given `message`'s content, and calls a command if
    found, or an other specified event.

    > Details under ``CommandProcesser``'s own docs.

    Arguments
    ---------
    client : ``Client``
        The client, who received the message.
    message : ``Message``
        The received message.

    Raises
    ------
    Any
    """
    await self.call_waitfors(client, message)

    if message.author.is_bot:
        return

    result = await self.prefixfilter(message)

    if result is None:
        # start goto if needed
        while self.mention_prefix:
            mentions = message.mentions
            if mentions is None:
                break

            if client not in message.mentions:
                break

            result = USER_MENTION_RP.match(message.content)
            if result is None or int(result.group(1)) != client.id:
                break

            result = COMMAND_RP.match(message.content, result.end())
            if result is None:
                break

            command_name, content = result.groups()
            command_name = command_name.lower()

            try:
                command = self.commands[command_name]
            except KeyError:
                break

            try:
                result = await command(client, message, content)
            except BaseException as err:
                command_error = self._command_error
                if command_error is not None:
                    checks = self._command_error_checks
                    if checks is None:
                        await command_error(client, message, command, content, err)
                        return
                    else:
                        for check in checks:
                            if await check(client, message):
                                continue

                            handler = check.handler
                            if handler is not None:
                                await handler(client, message, command, check)
                            break
                        else:
                            await command_error(client, message, command, content, err)
                            return

                await client.events.error(client, repr(self), err)
                return

            else:
                if result:
                    return

            break

    else:
        command_name, content = result
        command_name = command_name.lower()

        try:
            command = self.commands[command_name]
        except KeyError:
            invalid_command = self._invalid_command
            if invalid_command is not None:
                checks = self._invalid_command_checks
                if checks is not None:
                    for check in checks:
                        if await check(client, message):
                            continue

                        handler = check.handler
                        if handler is not None:
                            await handler(client, message, command_name, check)
                        return

                await invalid_command(client, message, command_name, content)

            return

        try:
            result = await command(client, message, content)
        except BaseException as err:
            command_error = self._command_error
            if command_error is not None:
                checks = self._command_error_checks
                if checks is None:
                    await command_error(client, message, command_name, content, err)
                    return
                else:
                    for check in checks:
                        if await check(client, message):
                            continue

                        handler = check.handler
                        if handler is not None:
                            await handler(client, message, command_name, check)
                        break
                    else:
                        await command_error(client, message, command_name, content, err)
                        return

            await client.events.error(client, repr(self), err)
            return

        else:
            if result:
                return

            invalid_command = self._invalid_command
            if invalid_command is not None:
                checks = self._invalid_command_checks
                if checks is not None:
                    for check in checks:
                        if await check(client, message):
                            continue

                        handler = check.handler
                        if handler is not None:
                            await handler(client, message, command_name, check)
                        return

                await invalid_command(client, message, command_name, content)

            return

    default_event = self._default_event
    if default_event is not None:
        await default_event(client, message)


CommandProcesser.__call__ = __call__
