import tkinter as tk
from tkinter import ttk  # For the ComboBox
import sounddevice as sd
import numpy as np
import queue
import threading
import time
from scipy.signal import find_peaks

# Configuration
fs = 44100  # Sampling frequency
unit_duration = 0.09 # Duration of the dot in seconds
morse_freq = 2000  # Frequency for the Morse code
listening = True  # Initial state
transmitting = False  # Transmission state
stream = None  # Variable for the audio stream
temps_mitja_per_lletra = 2

# Morse dictionary
morse_code = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.',
    'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-',
    'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..', '1': '.----',
    '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', '0': '-----', ' ': '/'
}

# Reverse Morse dictionary
morse_to_text = {v: k for k, v in morse_code.items()}

# Queue to manage incoming audio
q = queue.Queue()

# Define the root window globally
root = tk.Tk()

# Function to generate a sine wave tone
def generate_tone(frequency, duration):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)  # Adjusted amplitude
    return tone

# Function to play a tone
def play_tone(frequency, duration):
    tone = generate_tone(frequency, duration)
    sd.play(tone, samplerate=fs)
    sd.wait()

# Function to send a message (now in a separate thread)
def enviar_missatge():
    global listening, transmitting
    transmitting = True
    listening = False  # Stop listening while sending
    text = text_entry.get()  # Get user input text
    morse_text = text_to_morse(text)

    # Play the Morse code
    play_morse(morse_text)

    transmitting = False  # End transmission
    listening = True  # Resume listening

# Function to convert text to Morse code
def text_to_morse(text):
    morse_text = ''
    for char in text.upper():
        if char in morse_code:
            morse_text += morse_code[char] + ' '
    return morse_text

# Function to play Morse code with sounds
# Function to play Morse code with sounds
# Function to play Morse code with sounds
def play_morse(morse):
    for symbol in morse:
        if symbol == '.':  # Dot, now with 3000 Hz frequency and same duration as the dash
            play_tone(3000, unit_duration * 3)
            root.config(bg="#D0D0D9")
        elif symbol == '-':  # Dash, with 2000 Hz frequency
            play_tone(morse_freq, unit_duration * 3)
            root.config(bg="#D0D9D0")
        elif symbol == ' ':
            play_tone(4000, unit_duration * 3)  # 4000 Hz for spaces between words
            root.config(bg="#D0D0D0")
        time.sleep(unit_duration)  # Space between symbols within a letter
    
    # Play the final tone of 4800 Hz to signal translation
    play_tone(4800, unit_duration * 3)
    root.config(bg="light gray")


# Function to handle incoming audio
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Error in the audio stream: {status}")
    q.put(indata.copy())

# Function to detect the dominant frequency in audio
def detect_frequency(block):
    fft_result = np.fft.rfft(block[:, 0])  # Fourier Transform
    freqs = np.fft.rfftfreq(len(block), 1 / fs)  # Frequency list
    peak_indices, _ = find_peaks(np.abs(fft_result), height=10)  # Peak points of the FFT

    if len(peak_indices) > 0:
        dominant_freq = freqs[peak_indices[0]]  # Get the most dominant frequency
        return dominant_freq
    return None


# Function to interpret the received Morse code and convert it to text
def interpret_morse(morse_message):
    words = morse_message.strip().split('/')  # Separate by words (detected as '/')
    translated_message = ' '.join([''.join([morse_to_text.get(char, '') for char in word.split()]) for word in words])  # Translate each word
    return translated_message


def play_separator_tone():
    play_tone(4000, unit_duration)  # Generar un tono de 4000 Hz para separar letras
# Function to process incoming audio and display Morse code
# Function to process incoming audio and display Morse code
def process_audio():
    global listening, morse_message
    morse_message = ""  # Accumulated Morse message
    last_signal_time = time.time()
    previous_symbol_time = time.time()  # Time of the last detected symbol
    previous_symbol = None  # Save the last detected symbol (dot or dash)

    while True:
        block = q.get()
        if not listening:
            continue  # Skip processing if we're transmitting

        amplitude = np.linalg.norm(block)  # Calculate the audio amplitude
        dominant_freq = detect_frequency(block)

        # Update the audio level bar in the main thread
        root.after(0, update_audio_level, amplitude)

        current_time = time.time()
        time_since_last_signal = current_time - last_signal_time

        # If we detect a valid symbol (dot or dash)
        if amplitude > 0.01 and dominant_freq:
            last_signal_time = current_time

            # Detect a dot (3000 Hz)
            if 2900 < dominant_freq < 3100:  # Dot detected
                if time_since_last_signal > unit_duration:  # Only register after significant silence
                    morse_message += '.'
                    print("Dot detected")
                    root.after(0, update_received_message, '.')  # Update the GUI
                    previous_symbol_time = current_time
                    previous_symbol = '.'

            # Detect a dash (2000 Hz)
            elif 1900 < dominant_freq < 2100:  # Dash detected
                if time_since_last_signal > unit_duration:  # Only register after significant silence
                    morse_message += '-'
                    print("Dash detected")
                    root.after(0, update_received_message, '-')  # Update the GUI
                    previous_symbol_time = current_time
                    previous_symbol = '-'

            # Detect a space between words (4000 Hz)
            elif 3900 < dominant_freq < 4100:  # Space detected
                if previous_symbol != '/':  # Only register if the symbol has changed
                    morse_message += '/'
                    print("Space detected")
                    root.after(0, update_received_message, '/')  # Update the GUI
                    previous_symbol = '/'  # Save the symbol as the last detected one

            # Detect the final tone to trigger translation (4800 Hz ± 100)
            elif 4700 < dominant_freq < 4900:  # End signal detected
                if previous_symbol != 'traduzido':
                    print("End signal detected (4800 Hz)")
                    # Translate Morse code to text
                    translated_message = interpret_morse(morse_message)
                    print(f"Translated message: {translated_message}")

                # Update the GUI with the translated message
                    root.after(0, update_translated_message, translated_message)

                # Clear the accumulated Morse message after translation
                    morse_message = ""
                    previous_symbol = 'traduzido'
                    # If we detect a valid symbol (dot or dash)
            if amplitude > 0.01 and dominant_freq:
                root.after(0, update_detected_frequency, dominant_freq)  # Update the detected frequency in the GUI
                last_signal_time = current_time


        # If no signal, this is interpreted as silence
        else:
            # If enough time has passed without a signal, consider the end of a symbol
            if time_since_last_signal > unit_duration * 2:
                previous_symbol = None  # Reset the last detected symbol to allow the next


# Function to update the detected frequency in the GUI
def update_detected_frequency(frequency):
    frequency_label.config(text=f"Detected Frequency: {frequency:.2f} Hz")

def update_translated_message(message):
    # Update the translated text box by appending the new message
    translated_message_text.config(state=tk.NORMAL)
    translated_message_text.insert(tk.END, message + "\n")  # Append new translated message on a new line
    translated_message_text.config(state=tk.DISABLED)

    # Clear the Morse code box after translation
    received_message_text.config(state=tk.NORMAL)
    received_message_text.delete('1.0', tk.END)  # Clear the Morse code after translation
    received_message_text.config(state=tk.DISABLED)
    
    print(f"Displayed translated message: {message}")

# Función para limpiar el área de texto en la GUI
def clear_received_message():
    received_message_text.config(state=tk.NORMAL)
    received_message_text.delete('1.0', tk.END)  # Limpiar todo el texto
    received_message_text.config(state=tk.DISABLED)


# Function to update the received message in the GUI (this runs on the main thread)
def update_received_message(symbol):
    received_message_text.config(state=tk.NORMAL)
    received_message_text.insert(tk.END, symbol)
    received_message_text.config(state=tk.DISABLED)

# Function to update the audio level bar
# Function to update the audio level bar (make sure it's in the main thread)
def update_audio_level(amplitude):
    scaled_amplitude = min(amplitude * 1000, 100)  # Scale the amplitude for the bar
    audio_level_bar['value'] = scaled_amplitude
# Function to list active input devices
def listar_dispositivos_activos():
    dispositivos = sd.query_devices()
    dispositivos_activos = [(idx, dispositivo['name']) for idx, dispositivo in enumerate(dispositivos)
                            if dispositivo['max_input_channels'] > 0 and dispositivo['hostapi'] == 0]  # Filter active devices
    return dispositivos_activos

# Select the input device
def seleccionar_dispositivo(indice):
    global stream
    try:
        # Stop the current stream if active
        if stream:
            stream.stop()
            stream.close()

        # Select input device only
        sd.default.device = (indice, None)
        print(f"Selected input device: {sd.query_devices(indice)['name']}")

        # Restart the audio stream with the new device
        iniciar_stream_audio()

    except Exception as e:
        print(f"Error selecting device: {e}")

# Start the audio stream
def iniciar_stream_audio():
    global stream
    try:
        stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=fs)
        stream.start()
        print("Audio stream started successfully")
    except Exception as e:
        print(f"Error starting audio stream: {e}")

# Funció per calcular el temps estimat
def calcular_temps_estim(text):
    num_lletres = len(text.replace(" ", ""))  # Excloem espais del càlcul
    temps_estim = num_lletres * temps_mitja_per_lletra
    return temps_estim

# Funció per actualitzar el temps estimat en pantalla
def actualitzar_temps_estim(*args):
    text = text_entry.get()
    temps_estim = calcular_temps_estim(text)
    estimated_time_label.config(text=f"Temps estimat: {temps_estim:0f} segons")

# Create the GUI
def crear_GUI():
    root.config(bg="light gray")
    global text_entry, estimated_time_label, received_message_text, translated_message_text, status_label, device_selector, audio_status_label, audio_level_bar, frequency_label

    
    root.title("Morse Code with Audio")

    # Temps mitjà per lletra
    temps_mitja_per_lletra = 2

    # Funció per calcular el temps estimat
    def calcular_temps_estim(text):
        num_lletres = len(text.replace(" ", ""))  # Excloem espais del càlcul
        temps_estim = num_lletres * temps_mitja_per_lletra
        return temps_estim

    # Funció per actualitzar el temps estimat en pantalla
    def actualitzar_temps_estim(*args):
        text = text_entry.get()
        temps_estim = calcular_temps_estim(text)
        estimated_time_label.config(text=f"Temps estimat: {temps_estim:.0f} segons")

    # Aplicar estil modern ttk
    style = ttk.Style()
    style.theme_use("clam")  # Tema modern
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TCombobox", font=("Helvetica", 12))
    
    separador = tk.Canvas(root, height=9, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=122)  # Ajustar la posición de la línea
    separador.pack(fill="x", padx=0, pady=0)
    # Entrada de text
    text_label = ttk.Label(root, text="Text a enviar:")
    text_label.pack(pady=10)

    text_entry = ttk.Entry(root, width=50, font=("Helvetica", 12))
    text_entry.pack(pady=5)

    # Vincular l'entrada de text per actualitzar automàticament el temps estimat
    text_entry.bind("<KeyRelease>", actualitzar_temps_estim)

    # Etiqueta per mostrar el temps estimat
    estimated_time_label = ttk.Label(root, text="Temps estimat: 0.00 segons")
    estimated_time_label.pack(pady=5)

    # Botó per enviar el missatge
    send_button = ttk.Button(root, text="Enviar Missatge", command=lambda: threading.Thread(target=enviar_missatge).start())
    send_button.pack(pady=5)
    
    separador = tk.Canvas(root, height=1.5, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=122)  # Ajustar la posición de la línea
    separador.pack(fill="x", padx=0, pady=5)
    # Selecció de dispositiu d'entrada
    device_label = ttk.Label(root, text="Selecciona el micròfon:")
    device_label.pack(pady=10)

    dispositivos_activos = listar_dispositivos_activos()
    device_selector = ttk.Combobox(root, values=[nombre for _, nombre in dispositivos_activos], state="readonly")
    device_selector.pack(pady=5)
    
    # Crear un separador horizontal usando un Canvas con color negro
    separador = tk.Canvas(root, height=1.5, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=122)  # Ajustar la posición de la línea
    separador.pack(fill="x", padx=0, pady=5)
    # Esdeveniment per canviar de dispositiu quan es selecciona
    def cambiar_dispositivo(event):
        indice = dispositivos_activos[device_selector.current()][0]
        seleccionar_dispositivo(indice)

    device_selector.bind("<<ComboboxSelected>>", cambiar_dispositivo)

    # Text box per missatge rebut en Morse
    received_message_label = ttk.Label(root, text="Codi Morse rebut:")
    received_message_label.pack(pady=10)

    received_message_text = tk.Text(root, height=5, width=50, font=("Helvetica", 12))
    received_message_text.pack(pady=5)
    received_message_text.config(state=tk.DISABLED)
    
    separador = tk.Canvas(root, height=1.5, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=122)  # Ajustar la posición de la línea
    separador.pack(fill="x", padx=0, pady=10)
    # Nova secció per text traduït
    translated_message_label = ttk.Label(root, text="Text traduït:")
    translated_message_label.pack(pady=10)

    translated_message_text = tk.Text(root, height=5, width=50, font=("Helvetica", 12))
    translated_message_text.pack(pady=5)
    translated_message_text.config(state=tk.DISABLED)  # Només lectura

    separador = tk.Canvas(root, height=1.5, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=122)  # Ajustar la posición de la línea
    separador.pack(fill="x", padx=0, pady=10)
    # Etiqueta d'estat de l'àudio
    audio_status_label = ttk.Label(root, text="Nivell d'àudio:")
    audio_status_label.pack(pady=5)
    # Barra de nivell d'àudio
    audio_level_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
    audio_level_bar.pack(pady=10)

    separador = tk.Canvas(root, height=1.5, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=122)  # Ajustar la posición de la línea
    separador.pack(fill="x", padx=0, pady=10)

    # Etiqueta de freqüència detectada
    frequency_label = ttk.Label(root, text="Freqüència detectada: N/A")
    frequency_label.pack(pady=5)
    
    separador = tk.Canvas(root, height=20, bg="#D3D3D3", highlightthickness=0)
    separador.create_line(0, 0, 3000, 0, fill="dark gray", width=10)  # Ajustar la posición y grosor de la línea
    separador.pack(side='bottom', fill='x', padx=0, pady=0)  # Pegado al fondo y responsivo horizontalmente

    
    root.geometry("500x730")  # Ajusta la mida de la finestra
    root.mainloop()


# Start the application
if __name__ == "__main__":
    # Start audio processing in a separate thread
    threading.Thread(target=process_audio, daemon=True).start()
    # Start the GUI
    crear_GUI()
    # Start the audio stream
    iniciar_stream_audio()
