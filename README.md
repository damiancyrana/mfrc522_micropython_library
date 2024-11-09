# MFRC522 - A MicroPython Library for the MFRC522 RFID Reader

## Description
The `MFRC522` library is designed to facilitate the use of the MFRC522 RFID reader module in a MicroPython environment, specifically for use with the Raspberry Pi Pico. It provides a set of functions to read, write, authenticate, and communicate with RFID cards. This library aims to simplify interaction with RFID cards and tags, making it accessible for both beginners and experienced developers.

The MFRC522 RFID reader is commonly used in various applications, including access control systems, attendance systems, and other automation tasks that require identification through RFID cards or tags. This library abstracts the complexities of low-level SPI communication, allowing users to quickly implement RFID-based projects without needing in-depth knowledge of the underlying protocol.

## Features
- **Card Detection:** Easily detect RFID cards in the reader's range.
- **UID Reading:** Read the unique identifier (UID) of an RFID card.
- **Authentication and Data Access:** Authenticate to access specific blocks of data on MIFARE Classic cards.
- **Data Reading and Writing:** Read and write data to specified blocks on RFID cards.
- **Error Handling:** Robust error handling for authentication, reading, and writing operations.

## Installation
The `MFRC522` library can be installed via PyPI. Use the following command to install it:

```sh
pip install mfrc522
```

Make sure you have the appropriate environment for MicroPython setup on your Raspberry Pi Pico before installing.

## Hardware Requirements
- **Raspberry Pi Pico**: This library is intended to run on the Raspberry Pi Pico using MicroPython.
- **MFRC522 RFID Reader Module**: A compatible MFRC522 module with SPI interface.
- **RFID Cards or Tags**: MIFARE Classic cards are supported.
- **Wires and Breadboard**: For wiring the RFID reader to the Pico.

### Pin Connections
To connect the MFRC522 module to the Raspberry Pi Pico, use the following configuration:
- **SCK**: GPIO 18 (SPI0 SCK)
- **MISO**: GPIO 16 (SPI0 MISO)
- **MOSI**: GPIO 19 (SPI0 MOSI)
- **CS**: GPIO 17 (Chip Select)
- **RST**: GPIO 22 (Reset)
- **VCC**: 3.3V
- **GND**: GND

Ensure that the Pico and the MFRC522 module share a common ground.

## Example Usage
Here is an example of how to use the `MFRC522` library to interact with an RFID card. The script reads the UID of a card when it is placed near the reader.

```python
from machine import Pin, SPI
from mfrc522_micropython.mfrc522 import MFRC522
from time import sleep

# Initialize SPI and pins
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)
rst = Pin(22, Pin.OUT)

# Use context manager for proper resource management
with MFRC522(spi, cs, rst) as reader:
    print("Place a card near the reader")

    card_detected = False  # To track the previous state
    while True:
        uid = reader.read_uid()
        if uid:
            if not card_detected:
                # Print only once when the card is first detected
                print("Card UID:", " ".join("{:02X}".format(i) for i in uid))
                card_detected = True
                break
        else:
            if card_detected:
                # If previously a card was detected and now it is not
                print("No card detected")
                card_detected = False
        sleep(0.5)
```
### Explanation:
1. **SPI Initialization**: The SPI interface is initialized using the `machine.SPI` class with specified GPIO pins.
2. **MFRC522 Initialization**: The `MFRC522` class is used to create a reader instance, which handles communication with the RFID reader.
3. **Card Detection**: The program runs in a loop until it detects an RFID card, and once detected, it reads and prints the UID of the card.

## Dependencies
- **MicroPython**: This library requires MicroPython to be installed on your Raspberry Pi Pico.
- **`machine` Module**: The library relies on the `machine` module for handling SPI and GPIO pins.
- **SPI Communication**: The MFRC522 communicates with the Raspberry Pi Pico via SPI, so ensure proper SPI wiring and configuration.

## Additional Information
If you encounter any issues, ensure that your wiring is correct and that the Raspberry Pi Pico is running the correct version of MicroPython. For additional help, please refer to the [official documentation](https://micropython.org/doc/) for MicroPython and [MFRC522 Datasheet](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf).

## Author
**Damian Cyrana**  
[GitHub Profile](https://github.com/damiancyrana)

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

