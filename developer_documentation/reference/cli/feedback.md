# Feedback Command

The `feedback` command allows users to submit feedback, bug reports, and feature requests directly from the CLI.

## Usage

```bash
lattice-lock feedback [COMMAND] [OPTIONS]
```

## Commands

### `submit`

Submit a new feedback item.

```bash
lattice-lock feedback submit "The compiler is too slow on large projects" --type issue
```

### `list`

List submitted feedback.

```bash
lattice-lock feedback list
```
