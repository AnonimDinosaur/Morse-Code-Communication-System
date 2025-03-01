# Frequency-Based Morse Code Transmission

## Description

This project enables communication between computers using ultrasonic frequencies to transmit and receive Morse code messages. It does not require the internet or physical cables, making it useful for offline messaging systems.

## Features

- **Real-time transmission and reception** of Morse code using sound waves.
- **Customizable frequency settings** for improved flexibility.
- **Automatic message detection** when a specific tone is received.
- **Graphical user interface (GUI)** for easy interaction.
- **Live audio monitoring** with visual indicators for sound levels and frequency detection.

## How It Works

1. **Transmission:** The sender converts a text message into Morse code and transmits it using sound frequencies above 20,000 Hz (inaudible to humans).
2. **Detection:** The receiver listens for a specific activation tone (500 Hz for 2 seconds) to start recording Morse code.
3. **Decoding:** The system translates the received frequencies back into text based on predefined Morse code patterns.
4. **Display:** The decoded message is displayed on the user interface.

## Installation

### Prerequisites

- **Python 3.x**
- Required libraries:
  ```sh
  pip install sounddevice numpy scipy tkinter queue threading time
  ```

### Running the Application

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/frequency-morse-code.git
   ```
2. Navigate to the project folder:
   ```sh
   cd frequency-morse-code
   ```
3. Run the main script:
   ```sh
   python main.py
   ```

## Usage
  ![Captura de pantalla 2025-03-01 212758](https://github.com/user-attachments/assets/0c71c9d1-cbcd-487a-83a9-a6a7ba7c05b9)

### Sending a Message

1. Enter your text message in the input box.
2. Click **"Send Message"** to convert it into Morse code and transmit it using sound waves.

### Receiving a Message

1. The system continuously listens for a 500 Hz activation tone.
2. Once detected, it starts receiving Morse code signals.
3. The decoded message appears in the "Translated Text" section.

## Customization

You can modify the frequency settings in the script to suit your needs:

- **Activation tone:** Default is 500 Hz.
- **Morse code frequencies:** Default isn't a range of ultrasonic frequencies you need to adjust ur wanted frequencies.
- **Transmission speed:** Adjust the timing to control the speed of character transmission.

## Known Issues

- Background noise may interfere with signal detection.
- Some microphones and speakers may not support ultrasonic frequencies (thats why default isnt ultrasonic).

## Future Improvements

- Implement noise reduction filters.
- Add support for different Morse code speeds.
- Improve error handling and signal correction.

## License

This project is open-source under the MIT License.

## Contact

For questions or contributions, feel free to reach out via GitHub Issues.

coldagsala\@gmail.com
