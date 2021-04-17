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

    python3 secure-dealer.py deal input

Where `input` is the name of the input directory containing the files described above

### To peek

    python3 secure-dealer.py peek output

Where `output` is the name of the output directory created by `secure-dealer.py deal`

### For more options

    python3 secure-dealer.py -h

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
        "fingerprint": "568EFBC76B190F6EBB9E58A21E9CDA0AAB0D6D91",
        "encrypted_data": "player2.gpg"
    }
}
```

Where `player1.pgp` and `player2.pgp` are pgp-encrypted files containing the hidden identities of each respective player.
These files can only be decrypted by the concerned players (or whoever has their private keys) as well as the admins specified in the `input.json` file.

Decrypting the files can be done, as always, by running

    gpg -d file_to_decrypt.pgp


```
❯ gpg -d output/player1.gpg
gpg: encrypted with 4096-bit RSA key, ID D5B027D523AA3BB2, created 2018-03-29
      "xxxx <xxxx@xxxx.com>"
gpg: encrypted with 2048-bit RSA key, ID 3A16C01089A32E9A, created 2020-03-11
      "zzzz <zzzz@zzzz.com>"
Player1
================
Name: HiddenIdentity2
Password: None
```

```
❯ gpg -d output/player2.gpg
gpg: encrypted with 3072-bit RSA key, ID F1356AF30BB9F3F1, created 2021-04-12
      "yyyy <yyyy@yyyy.com>"
gpg: encrypted with 2048-bit RSA key, ID 3A16C01089A32E9A, created 2020-03-11
      "zzzz <zzzz@zzzz.com>"
Player2
================
Name: HiddenIdentity1
Password: None
```

## Authors

  - **Theodor Dimov** - *Initial work* -
    [GitHub](https://github.com/tdimov93)
