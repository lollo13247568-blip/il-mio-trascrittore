import streamlit as st
from num2words import num2words
import speech_recognition as sr
from moviepy import AudioFileClip
import os
import math

st.set_page_config(page_title="Super Trascrittore AI", page_icon="🔐", layout="centered")

PASSWORD_CORRETTA = "Segreto2026"

def verifica_accesso():
    if "connesso" not in st.session_state:
        st.session_state["connesso"] = False
    if not st.session_state["connesso"]:
        st.title("🔒 Accesso Limitato")
        chiave = st.text_input("Inserisci Password:", type="password")
        if st.button("Sblocca Sito"):
            if chiave == PASSWORD_CORRETTA:
                st.session_state["connesso"] = True
                st.rerun()
            else:
                st.error("❌ Password errata.")
        return False
    return True

if verifica_accesso():
    st.title("🎙️ Trascrittore Audio & Video per File Lunghi")
    st.write("Carica un file audio (.mp3, .wav) o un video (.mp4) senza limiti di durata.")
    
    file_caricato = st.file_uploader("Scegli un file:", type=["wav", "mp3", "mp4"])
    
    if st.button("Avvia Trascrizione 🚀"):
        if file_caricato is None:
            st.warning("Per favore, carica un file.")
        else:
            with st.spinner("Estrazione dell'audio in corso..."):
                try:
                    # 1. Salva il file originale
                    nome_file_temp = file_caricato.name
                    with open(nome_file_temp, "wb") as f:
                        f.write(file_caricato.getbuffer())
                    
                    file_wav_intero = "intero_temp.wav"
                    
                    # 2. Estrai l'audio completo con MoviePy
                    clip = AudioFileClip(nome_file_temp)
                    durata_totale = clip.duration  # Durata in secondi
                    clip.write_audiofile(file_wav_intero, logger=None)
                    clip.close()
                    
                    # 3. Spezzetta e trascrivi (blocchi da 30 secondi)
                    riconoscitore = sr.Recognizer()
                    testo_finale = []
                    
                    # Calcola quanti pezzi da 30 secondi servono
                    durata_blocco = 30
                    pezzi_totali = math.ceil(durata_totale / durata_blocco)
                    
                    barra_progresso = st.progress(0)
                    testo_stato = st.empty()
                    
                    with sr.AudioFile(file_wav_intero) as sorgente:
                        for i in range(pezzi_totali):
                            testo_stato.write(f"Trascrizione parte {i+1} di {pezzi_totali}...")
                            
                            # Registra solo il blocco di 30 secondi corrente
                            dati_audio = riconoscitore.record(sorgente, duration=durata_blocco)
                            
                            try:
                                # Trascrivi il singolo pezzo
                                testo_pezzo = riconoscitore.recognize_google(dati_audio, language="it-IT")
                                testo_finale.append(testo_pezzo)
                            except sr.UnknownValueError:
                                # Se in questi 30 secondi c'è solo silenzio, salta senza dare errore
                                pass
                            except Exception as e:
                                testo_finale.append(f"[Errore in questa parte: {e}]")
                            
                            # Aggiorna la barra di caricamento visiva sul sito
                            barra_progresso.progress((i + 1) / pezzi_totali)
                    
                    testo_stato.empty()
                    barra_progresso.empty()
                    
                    # 4. Mostra il risultato unito
                    st.success("Trascrizione completata con successo!")
                    risultato_testo = " ".join(testo_finale)
                    st.text_area("Testo rilevato:", value=risultato_testo, height=300)
                    
                    # Pulizia dei file temporanei
                    os.remove(nome_file_temp)
                    os.remove(file_wav_intero)
                    
                except Exception as e:
                    st.error(f"Errore durante l'elaborazione: {e}")
