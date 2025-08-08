#!/bin/bash
# Setup script for Haro on Raspberry Pi

set -e

echo "================================================================"
echo "              Haro - Raspberry Pi Setup Script"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if grep -q "Raspberry Pi" /proc/cpuinfo || grep -q "BCM" /proc/cpuinfo; then
        print_success "Raspberry Pi detected"
        return 0
    else
        print_warning "Not running on Raspberry Pi - some features may not work"
        return 1
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update -y
    sudo apt upgrade -y
    print_success "System packages updated"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Core development tools
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        git \
        curl \
        wget
    
    # Audio system dependencies
    sudo apt install -y \
        portaudio19-dev \
        python3-pyaudio \
        alsa-utils \
        pulseaudio \
        pulseaudio-utils \
        libasound2-dev
    
    # Text-to-speech dependencies
    sudo apt install -y \
        espeak \
        espeak-data \
        libespeak-dev \
        festival \
        festvox-kallpc16k
    
    print_success "System dependencies installed"
}

# Configure audio system
configure_audio() {
    print_status "Configuring audio system..."
    
    # Add user to audio group
    sudo usermod -a -G audio $USER
    
    # Configure ALSA
    if [ ! -f ~/.asoundrc ]; then
        cat > ~/.asoundrc << 'EOF'
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}
EOF
        print_status "Created ALSA configuration"
    fi
    
    # Start and enable audio services
    sudo systemctl --user enable pulseaudio
    sudo systemctl --user start pulseaudio
    
    print_success "Audio system configured"
}

# Create Python virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    
    if [ ! -d "companion_env" ]; then
        python3 -m venv companion_env
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate and upgrade pip
    source companion_env/bin/activate
    pip install --upgrade pip
    pip install wheel setuptools
    
    print_success "Virtual environment ready"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    source companion_env/bin/activate
    
    # Install core dependencies
    pip install openai>=1.3.0
    pip install SpeechRecognition>=3.10.0
    pip install pyttsx3>=2.90
    pip install psutil>=5.9.0
    
    # Try to install PyAudio (may need special handling on Pi)
    if ! pip install pyaudio>=0.2.11; then
        print_warning "Failed to install PyAudio via pip, trying system package"
        sudo apt install -y python3-pyaudio
    fi
    
    # Install Raspberry Pi specific packages if on Pi
    if check_raspberry_pi; then
        print_status "Installing Raspberry Pi specific packages..."
        pip install RPi.GPIO>=0.7.1 || print_warning "Could not install RPi.GPIO"
        pip install gpiozero>=1.6.2 || print_warning "Could not install gpiozero"
    fi
    
    print_success "Python dependencies installed"
}

# Test audio setup
test_audio() {
    print_status "Testing audio setup..."
    
    # Test microphone
    print_status "Testing microphone (recording 3 seconds)..."
    if timeout 5 arecord -d 3 -f cd /tmp/test_mic.wav > /dev/null 2>&1; then
        print_success "Microphone test passed"
        rm -f /tmp/test_mic.wav
    else
        print_error "Microphone test failed"
        print_warning "Please check microphone connection and permissions"
    fi
    
    # Test speakers
    print_status "Testing speakers..."
    if which speaker-test > /dev/null; then
        print_status "Run 'speaker-test -t sine -f 1000 -l 1' to test speakers manually"
    fi
    
    # Test text-to-speech
    print_status "Testing text-to-speech..."
    if which espeak > /dev/null; then
        echo "Testing espeak..." | espeak 2>/dev/null || print_warning "Espeak test failed"
    fi
}

# Create systemd service (optional)
create_service() {
    if [ "$1" = "--service" ]; then
        print_status "Creating systemd service..."
        
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        
        sudo tee /etc/systemd/system/haro-ai.service > /dev/null << EOF
[Unit]
Description=Haro Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/companion_env/bin
ExecStart=$SCRIPT_DIR/companion_env/bin/python -m companion_ai.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable haro-ai.service
        
        print_success "Systemd service created and enabled"
        print_status "Use 'sudo systemctl start haro-ai' to start the service"
    fi
}

# Setup AI mode configuration
setup_ai_mode() {
    print_status "Setting up AI mode configuration..."
    
    echo "Choose your AI mode:"
    echo "1. Local (FREE) - Works completely offline, no API key needed"
    echo "2. OpenAI - Requires API key but more advanced conversations"
    echo
    
    # Default to local mode for free operation
    if [ -z "$AI_MODE" ]; then
        print_status "Defaulting to LOCAL mode (free operation)"
        echo 'export AI_MODE="local"' >> ~/.bashrc
        export AI_MODE="local"
    fi
    
    if [ "$AI_MODE" = "openai" ]; then
        if [ -z "$OPENAI_API_KEY" ]; then
            print_warning "OpenAI mode selected but OPENAI_API_KEY not set"
            echo "Please set your OpenAI API key:"
            echo "export OPENAI_API_KEY='your-api-key-here'"
            echo "To make it permanent:"
            echo "echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
        else
            print_success "OpenAI API key is set"
        fi
    else
        print_success "Local mode configured - Haro will work completely FREE!"
    fi
}

# Create desktop shortcut (optional)
create_desktop_shortcut() {
    if [ "$1" = "--desktop" ]; then
        print_status "Creating desktop shortcut..."
        
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        DESKTOP_FILE="$HOME/Desktop/haro-ai.desktop"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Haro
Comment=Voice-Activated AI Assistant
Exec=lxterminal -e "$SCRIPT_DIR/companion_env/bin/python -m companion_ai.main"
Icon=applications-science
Terminal=false
Type=Application
Categories=Utility;AudioVideo;
EOF
        
        chmod +x "$DESKTOP_FILE"
        print_success "Desktop shortcut created"
    fi
}

# Main setup function
main() {
    echo "Starting Haro setup..."
    echo
    
    # Parse arguments
    CREATE_SERVICE=false
    CREATE_DESKTOP=false
    
    for arg in "$@"; do
        case $arg in
            --service)
                CREATE_SERVICE=true
                ;;
            --desktop)
                CREATE_DESKTOP=true
                ;;
            --help)
                echo "Usage: $0 [--service] [--desktop]"
                echo "  --service  Create systemd service"
                echo "  --desktop  Create desktop shortcut"
                exit 0
                ;;
        esac
    done
    
    # Run setup steps
    check_raspberry_pi
    update_system
    install_system_deps
    configure_audio
    create_venv
    install_python_deps
    test_audio
    setup_ai_mode
    
    if [ "$CREATE_SERVICE" = true ]; then
        create_service --service
    fi
    
    if [ "$CREATE_DESKTOP" = true ]; then
        create_desktop_shortcut --desktop
    fi
    
    echo
    print_success "Haro setup complete!"
    echo
    echo "Next steps:"
    echo "1. Haro is ready to run in LOCAL mode (FREE!)"
    echo "2. Reboot or logout/login for audio group changes"
    echo "3. Test the installation:"
    echo "   source companion_env/bin/activate"
    echo "   python -m companion_ai.main --test"
    echo "4. Run the full voice assistant:"
    echo "   python -m companion_ai.main"
    echo "5. Optional: To switch to OpenAI mode later:"
    echo "   export AI_MODE=\"openai\" && export OPENAI_API_KEY=\"your-key\""
    echo
}

# Run main function with all arguments
main "$@"
