# Admin Command

The `admin` command allows management of users, API keys, and system configuration.

## Usage

```bash
lattice-lock admin [COMMAND] [OPTIONS]
```

## Commands

### `user`

Manage system users.

```bash
# Create a new user
lattice-lock admin user create --username alice --role developer

# Reset password
lattice-lock admin user reset-password --username alice
```

### `apikey`

Manage API keys.

```bash
# specific key generation
lattice-lock admin apikey create --name "ci-runner" --role operator
```

### `config`

View or update system configuration.

```bash
lattice-lock admin config show
```
