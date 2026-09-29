# Notify the user

When and what to notify, for every skill that notifies. The user steps away during a long run; a notification is how they know to come back.

## When

Exactly two moments:

- **Done:** the pull request is delivered: every ticket committed and pushed, the final review fixed, the description written.
- **Blocked:** nothing can continue without the user, and you are about to ask your one question (the **orchestrating** skill's *Talking to the user*).

Routine progress stays in the chat: a ticket landing, a delegate reporting, a wave starting.

## What

One line under 200 characters, leading with what the user acts on:

```text
PR ready for review: Effort workflow, 19 tickets, 2 decisions to check
blocked: "Sign in with the provider" needs your OAuth app client ID
```

Name tickets and pull requests by title, not by a number alone.

## How

The **Notifications** row of the Defaults table in the user's global instructions says how notifications reach them (for example, an `osascript` command on macOS because the harness's tool doesn't reach their terminal); follow it. With no row, or `none`, use the harness's built-in notification tool. With neither, skip the notification and say it in the chat.
