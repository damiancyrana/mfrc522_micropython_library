#####################################################
#                                                   #
#     RFID-RC522 module library for MicroPython     #
#     for Raspberry Pi Pico                         #
#                                                   #
#     Author:                                       #
#        Damian Cyrana                              #
#        https://github.com/damiancyrana            #
#                                                   #
#####################################################

from machine import Pin, SPI


class MFRC522Error(Exception):
    """Base exception class for MFRC522 errors"""


class AuthenticationError(MFRC522Error):
    """Exception raised for authentication errors"""


class ReadError(MFRC522Error):
    """Exception raised for read errors"""


class WriteError(MFRC522Error):
    """Exception raised for write errors"""


class MFRC522:
    """
    Class to interact with MFRC522 RFID reader using MicroPython
    """
    # MFRC522 Registers
    COMMAND_REG = 0x01
    COMM_IE_N_REG = 0x02
    DIV_I_EN_REG = 0x03
    COMM_IRQ_REG = 0x04
    DIV_IRQ_REG = 0x05
    ERROR_REG = 0x06
    STATUS1_REG = 0x07
    STATUS2_REG = 0x08
    FIFO_DATA_REG = 0x09
    FIFO_LEVEL_REG = 0x0A
    WATER_LEVEL_REG = 0x0B
    CONTROL_REG = 0x0C
    BIT_FRAMING_REG = 0x0D
    COLL_REG = 0x0E
    MODE_REG = 0x11
    TX_MODE_REG = 0x12
    RX_MODE_REG = 0x13
    TX_CONTROL_REG = 0x14
    TX_AUTO_REG = 0x15
    T_MODE_REG = 0x2A
    T_PRESCALER_REG = 0x2B
    T_RELOAD_REG_H = 0x2C
    T_RELOAD_REG_L = 0x2D
    CRC_RESULT_REG_L = 0x22
    CRC_RESULT_REG_M = 0x21

    # MFRC522 Commands
    PCD_IDLE = 0x00
    PCD_AUTHENT = 0x0E
    PCD_RECEIVE = 0x08
    PCD_TRANSMIT = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC = 0x03

    # MIFARE Commands
    PICC_REQIDL = 0x26
    PICC_REQALL = 0x52
    PICC_ANTICOLL = 0x93
    PICC_SELECTTAG = 0x93
    PICC_AUTHENT1A = 0x60
    PICC_AUTHENT1B = 0x61
    PICC_READ = 0x30
    PICC_WRITE = 0xA0
    PICC_DECREMENT = 0xC0
    PICC_INCREMENT = 0xC1
    PICC_RESTORE = 0xC2
    PICC_TRANSFER = 0xB0
    PICC_HALT = 0x50

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    MAX_LEN = 16

    # Default keys
    DEFAULT_KEYS = [
        [0xFF] * 6,  # Factory default key
        [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5],
        [0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5],
        [0x4D, 0x3A, 0x99, 0xC3, 0x51, 0xDD],
        [0x1A, 0x98, 0x2C, 0x7E, 0x45, 0x9A],
        [0xAA] * 6,
        [0xBB] * 6,
        [0xCC] * 6,
        [0x00] * 6,
        [0xAB] * 6,
        [0xBC] * 6,
        [0x30] * 6,
        [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7],
        # Add more keys if you need
    ]

    def __init__(self, spi, cs, rst):
        """
        Initialize the MFRC522 reader

        Args:
            spi: SPI bus instance
            cs: Chip select pin
            rst: Reset pin
        """
        self.spi = spi
        self.cs = cs
        self.rst = rst
        self.cs.init(Pin.OUT, value=1)
        self.rst.init(Pin.OUT, value=1)
        self._init_reader()

    def _init_reader(self):
        """Initialize the MFRC522 reader"""
        self._reset()
        self._write_register(self.T_MODE_REG, 0x8D)
        self._write_register(self.T_PRESCALER_REG, 0x3E)
        self._write_register(self.T_RELOAD_REG_L, 30)
        self._write_register(self.T_RELOAD_REG_H, 0)
        self._write_register(self.TX_AUTO_REG, 0x40)
        self._write_register(self.MODE_REG, 0x3D)
        self._antenna_on()

    def _reset(self):
        """Reset the MFRC522 reader"""
        self._write_register(self.COMMAND_REG, self.PCD_RESETPHASE)

    def _write_register(self, addr, val):
        """Write a byte to a register

        Args:
            addr: Register address
            val: Value to write
        """
        self.cs.value(0)
        self.spi.write(bytearray([(addr << 1) & 0x7E]))
        self.spi.write(bytearray([val]))
        self.cs.value(1)

    def _read_register(self, addr):
        """Read a byte from a register

        Args:
            addr: Register address

        Returns:
            Value read from the register
        """
        self.cs.value(0)
        self.spi.write(bytearray([((addr << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0]

    def _set_bit_mask(self, reg, mask):
        """Set bits in a register

        Args:
            reg: Register address
            mask: Mask to set
        """
        tmp = self._read_register(reg)
        self._write_register(reg, tmp | mask)

    def _clear_bit_mask(self, reg, mask):
        """Clear bits in a register

        Args:
            reg: Register address
            mask: Mask to clear
        """
        tmp = self._read_register(reg)
        self._write_register(reg, tmp & (~mask))

    def _antenna_on(self):
        """Turn on the antenna"""
        temp = self._read_register(self.TX_CONTROL_REG)
        if not (temp & 0x03):
            self._set_bit_mask(self.TX_CONTROL_REG, 0x03)

    def _antenna_off(self):
        """Turn off the antenna"""
        self._clear_bit_mask(self.TX_CONTROL_REG, 0x03)

    def _calculate_crc(self, data):
        """Calculate CRC of data

        Args:
            data: Data to calculate CRC

        Returns:
            CRC high byte, CRC low byte
        """
        self._clear_bit_mask(self.DIV_IRQ_REG, 0x04)
        self._set_bit_mask(self.FIFO_LEVEL_REG, 0x80)
        for c in data:
            self._write_register(self.FIFO_DATA_REG, c)
        self._write_register(self.COMMAND_REG, self.PCD_CALCCRC)
        i = 0xFF
        while True:
            n = self._read_register(self.DIV_IRQ_REG)
            i -= 1
            if i == 0 or n & 0x04:
                break
        crc_result = (self._read_register(self.CRC_RESULT_REG_L),
                      self._read_register(self.CRC_RESULT_REG_M))
        return crc_result

    def _transceive(self, send_data):
        """Send data to card and receive response

        Args:
            send_data: Data to send

        Returns:
            Status, received data, received bits length
        """
        back_data = []
        back_len = 0
        status = self.MI_ERR

        self._write_register(self.COMM_IE_N_REG, 0x77)
        self._clear_bit_mask(self.COMM_IRQ_REG, 0x80)
        self._set_bit_mask(self.FIFO_LEVEL_REG, 0x80)
        self._write_register(self.COMMAND_REG, self.PCD_IDLE)

        for c in send_data:
            self._write_register(self.FIFO_DATA_REG, c)

        self._write_register(self.COMMAND_REG, self.PCD_TRANSCEIVE)
        self._set_bit_mask(self.BIT_FRAMING_REG, 0x80)

        i = 2000
        while True:
            n = self._read_register(self.COMM_IRQ_REG)
            i -= 1
            if not (i != 0 and not (n & 0x01) and not (n & 0x30)):
                break

        self._clear_bit_mask(self.BIT_FRAMING_REG, 0x80)

        if i != 0:
            error = self._read_register(self.ERROR_REG)
            if not (error & 0x1B):
                status = self.MI_OK
                if n & 0x01:
                    status = self.MI_NOTAGERR
                if n & 0x30:
                    back_len = self._read_register(self.FIFO_LEVEL_REG)
                    last_bits = self._read_register(self.CONTROL_REG) & 0x07
                    if last_bits != 0:
                        back_len = (back_len - 1) * 8 + last_bits
                    else:
                        back_len = back_len * 8
                    if back_len > self.MAX_LEN * 8:
                        back_len = self.MAX_LEN * 8
                    back_data = []
                    for _ in range(back_len // 8):
                        back_data.append(self._read_register(self.FIFO_DATA_REG))
            else:
                status = self.MI_ERR

        return status, back_data, back_len

    def request(self, req_mode):
        """
        Send a request to detect cards in the reader's range

        Args:
            req_mode: Request mode (PICC_REQIDL or PICC_REQALL)

        Returns:
            Status, ATQA response from the card
        """
        self._write_register(self.BIT_FRAMING_REG, 0x07)
        status, back_data, back_bits = self._transceive([req_mode])

        if (status != self.MI_OK) or (back_bits != 0x10):
            status = self.MI_ERR

        return status, back_data

    def anticoll(self):
        """
        Perform anti-collision to get the UID of a card

        Returns:
            Status, UID of the card
        """
        ser_num = [self.PICC_ANTICOLL, 0x20]
        self._write_register(self.BIT_FRAMING_REG, 0x00)
        status, back_data, back_bits = self._transceive(ser_num)

        uid = []
        if status == self.MI_OK:
            if len(back_data) == 5:
                checksum = 0
                for i in range(4):
                    checksum ^= back_data[i]
                if checksum != back_data[4]:
                    status = self.MI_ERR
                else:
                    uid = back_data[:4]
            else:
                status = self.MI_ERR

        return status, uid

    def select_tag(self, uid):
        """
        Select a card by its UID

        Args:
            uid: UID of the card

        Returns:
            SAK response from the card
        """
        buf = [self.PICC_SELECTTAG, 0x70] + uid
        crc = self._calculate_crc(buf)
        buf += crc
        status, back_data, back_len = self._transceive(buf)
        if (status == self.MI_OK) and (back_len == 0x18):
            return back_data[0]
        else:
            return 0

    def authenticate(self, auth_mode, block_addr, key, uid):
        """
        Authenticate with a sector of the card

        Args:
            auth_mode: Authentication mode (PICC_AUTHENT1A or PICC_AUTHENT1B)
            block_addr: Block address
            key: Key for authentication
            uid: UID of the card

        Raises:
            AuthenticationError: If authentication fails
        """
        buff = [auth_mode, block_addr] + key + uid[:4]
        status, back_data, back_len = self._transceive(buff)
        if status != self.MI_OK or not (self._read_register(self.STATUS2_REG) & 0x08):
            raise AuthenticationError("Authentication failed")

    def stop_crypto1(self):
        """Stop encrypted communication with the card"""
        self._clear_bit_mask(self.STATUS2_REG, 0x08)

    def read(self, block_addr):
        """
        Read data from a block

        Args:
            block_addr: Block address

        Returns:
            Data read from the block

        Raises:
            ReadError: If read fails
        """
        recv_data = [self.PICC_READ, block_addr]
        crc = self._calculate_crc(recv_data)
        recv_data += crc
        status, back_data, back_len = self._transceive(recv_data)
        if status == self.MI_OK and len(back_data) == 16:
            return back_data
        else:
            raise ReadError("Failed to read block {}".format(block_addr))

    def write(self, block_addr, data):
        """
        Write data to a block

        Args:
            block_addr: Block address
            data: Data to write (16 bytes)

        Raises:
            WriteError: If write fails
        """
        buf = [self.PICC_WRITE, block_addr]
        crc = self._calculate_crc(buf)
        buf += crc
        status, back_data, back_len = self._transceive(buf)
        if not (status == self.MI_OK) or not (back_len == 4) or not ((back_data[0] & 0x0F) == 0x0A):
            raise WriteError("Failed to initiate write")

        buf = data[:16]
        crc = self._calculate_crc(buf)
        buf += crc
        status, back_data, back_len = self._transceive(buf)
        if not (status == self.MI_OK) or not (back_len == 4) or not ((back_data[0] & 0x0F) == 0x0A):
            raise WriteError("Failed to write data")

    def read_uid(self):
        """
        Read UID of a card

        Returns:
            UID of the card if found, else None
        """
        status, _ = self.request(self.PICC_REQIDL)
        if status == self.MI_OK:
            status, uid = self.anticoll()
            if status == self.MI_OK:
                return uid
        return None

    def identify_card_type(self, atqa, sak):
        """
        Identify the card type based on ATQA and SAK

        Args:
            atqa: ATQA response
            sak: SAK response

        Returns:
            Type of the card
        """
        atqa_value = atqa[1] << 8 | atqa[0]
        sak_value = sak

        # Card types based on ATQA and SAK
        card_types = {
            (0x4400, 0x04): "MIFARE Ultralight",
            (0x0400, 0x09): "MIFARE Mini",
            (0x0400, 0x08): "MIFARE Classic 1K",
            (0x0200, 0x18): "MIFARE Classic 4K",
            (0x4403, 0x28): "MIFARE DESFire",
            (0x0800, 0x00): "MIFARE Plus",
            (0x0400, 0x00): "MIFARE Plus",
            (0x0400, 0x24): "MIFARE Ultralight C",
            (0x0400, 0x34): "MIFARE Ultralight EV1",
            (0x4400, 0x00): "NFC Forum Tag Type 2",
        }
        return card_types.get((atqa_value, sak_value), "Unknown card type")

    def __enter__(self):
        """Enter context manager"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager and clean up"""
        self._antenna_off()


