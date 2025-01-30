# Cache Optimizing MCUNet via Loop Unrolling
This is a script to loop unroll the kernel multiplication of a layer of an MCUNet-Generated TinyEngine Network
This is the work of a bachelor thesis.



## Requirements

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Installation

0. Setup a MCUNet Network
0. Clone this repository
1. Setup Python using the requirements.txt


## Usage
Fill out the config.toml with the relevant information.
Locate the file to be loop unrolled and add comments:
```c
// Start
// Start End
// Loop Start
// Loop End
// End
```


Run the main script:
```bash
python generate_unroll.py
```
Use
```bash
python generate_unroll.py --help
```
for a list of available commands


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements
Special Thanks to the people enableing this thesis:
- My University: Karlsruhe Institute of Technology
- My Supervisor: Georgios Mentzos
