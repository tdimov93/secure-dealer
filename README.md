# Secure Dealer

Assigns each entry a randomly chosen name from a pre-determined pool and writes the information to a PGP-encrypted file that can only be decrypted by the entry\'s private key (and any specified master keys)


## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

### Prerequisites

To run the secure dealer you will need
- a list of entries/players
- a list of hidden identities to assign to each of the players (at random)
- a PGP key per player (public key)
- a config file that follows the schema

```json
{
    "players": [
        {
            "name": "Player1",
            "keyfile": "player1.pub"
        },
        {
            "name": "Player2",
            "keyfile": "player2.pub"
        }
    ],
    "pool": [
        "HiddenIdentity1",
        "HiddenIdentity2"
    ],
    "admins": [
        {
            "name": "admin1",
            "keyfile": "admin1.pub"
        },
        {
            "name": "admin2",
            "keyfile": "admin2.pub"
        }
    ]
}
```

### Installing

Installing the pip requierments

    python3 -m pip install --user -r requirements.txt


## Running

### To run the dealer/randomizer and generate encrypted files:

    python3 randomizer.py input

or

    python3 secre-dealer.py deal input

Where `input` is the name of the input directory containing the files described above

### To peek

    python3 secre-dealer.py peek output

Where `output` is the name of the output directory created by `secure-dealer.py deal`

### For more options

    python3 secre-dealer.py -h

or 

    python3 randomizer.py -h


### Example output

![Example otput](/images/example_output.png)

```json
{
    "Player1": {
        "fingerprint": "0307E27271318F707A88ACFCC9267C7B2D1B4B58",
        "encrypted_data": "player1.gpg"
    },
    "Player2": {
        "fingerprint": "0307E27271318F707A88ACFCC9267C7B2D1B4B58",
        "encrypted_data": "player2.gpg"
    }
}
```

Where `player1.pgp` and `player2.pgp` are pgp-encrypted files containing the hidden identities of each respective player.
These files can only be decrypted by the concerned players (or whoever has their private keys) as well as the admins specified in the `input.json` file.

Decrypting the files can be done, as always, by running

    gpg -d file_to_decrypt.pgp


## Authors

  - **Theodor Dimov** - *Initial work* -
    [GitHub](https://github.com/tdimov93)
