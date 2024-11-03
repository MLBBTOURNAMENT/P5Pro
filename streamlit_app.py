import streamlit as st
from PIL import Image
import os

def main():
    st.title("BPJS Game Information")
    
    # Add game description
    st.header("About the Game")
    st.write("""
    This is an educational game about BPJS (Badan Penyelenggara Jaminan Sosial).
    Players can learn about BPJS while playing an interactive platformer game.
    """)
    
    # Display game features
    st.header("Game Features")
    st.write("""
    - Interactive platformer gameplay
    - Educational quiz about BPJS
    - Virtual joystick controls
    - Double jump mechanics
    """)
    
    # Display game controls
    st.header("How to Play")
    st.write("""
    - Use virtual joystick for movement
    - Tap jump button to jump
    - Double tap jump for double jump
    - Interact with NPCs to answer BPJS questions
    """)
    
    # Add BPJS Quiz section
    st.header("Sample Quiz Questions")
    with st.expander("Click to see sample questions"):
        st.write("""
        1. Apa kepanjangan dari BPJS?
           - Badan Penyelenggara Jaminan Sosial
           - Badan Pelayanan Jaminan Sosial
           - Badan Pemberi Jaminan Sosial
           - Badan Penyedia Jaminan Sosial
        
        2. Berapa iuran BPJS Kesehatan kelas 3?
           - Rp35.000
           - Rp42.000
           - Rp50.000
           - Rp45.000
        """)
    
    # Add GitHub repository link
    st.header("Source Code")
    st.write("Check out the game source code on [GitHub](https://github.com/YourUsername/YourRepo)")
    
    # Add download instructions
    st.header("How to Download and Run")
    st.code("""
    1. Clone the repository:
       git clone https://github.com/YourUsername/YourRepo.git
    
    2. Install requirements:
       pip install -r requirements.txt
    
    3. Run the game:
       python main.py
    """)

if __name__ == "__main__":
    main()