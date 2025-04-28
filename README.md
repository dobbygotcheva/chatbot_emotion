# Emotion-Aware Chatbot

A sophisticated chatbot that detects and responds to emotions in user messages. The chatbot can analyze text for emotional content, track conversation history, and provide appropriate responses based on detected emotions.

## Quick Start Guide

### How to Run the Application

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python run.py
   ```

### How to Access the Application

When the application starts, it will display the URLs you can use to access it:
```
=== CHATBOT SERVER ADDRESS ===
Starting server on http://0.0.0.0:8081
You can access the application at:
  - Local: http://localhost:8081
  - Network: http://192.168.1.100:8081 (for other computers on the same network)
  - For remote access, deploy to a cloud hosting service.
  - See README.md for deployment instructions.
===============================
```

Simply open your web browser and navigate to:
- On the same computer: http://localhost:8081
- From other computers on the same network: Use the Network URL shown in the console

## Features

- Emotion detection with confidence scoring for 28 different emotions
- Mixed emotion analysis for complex messages
- Conversation history tracking
- Performance metrics for accuracy, latency, memory usage, and emotion coverage
- Visualization of performance metrics
- HTML report generation for presenting results

## Features (continued)
- Enhanced context-aware emotion detection for real-life texts
- Advanced pattern matching and sentiment analysis
- Implicit emotion detection in conversational context
- Handling of negation and complex emotional expressions
- Confidence scoring for emotion detection
- Real-time chat interface
- Responsive web design

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

   Or install dependencies directly:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your configuration:
   ```
   PORT=8081  # Default port is 8081, change if needed
   DATABASE_URL=sqlite:///app.db
   FLASK_ENV=development  # Use 'production' for production environment

   # For remote access, deploy to a cloud hosting service
   # See the "Remote Access" section below for details
   ```
5. Run the application:
   ```bash
   python run.py
   ```

   Or if installed as a package:
   ```bash
   python -m chatbot_app
   ```

## Usage

1. Open your web browser and navigate to:
   - On the same computer: `http://localhost:8081` (or the custom port you specified in your .env file)
   - From other computers on the same network: `http://<your-computer-ip>:8081` (the IP address will be displayed when you start the application)

   Note: The application uses HTTP by default. The server address will be displayed when you start the application.
2. Start chatting with the bot
3. The bot will detect your emotions and respond accordingly
4. Each response will show the detected emotion and confidence level

### Accessing from Other Computers

When you run the application, it will display the addresses that can be used to access it:

```
=== CHATBOT SERVER ADDRESS ===
Starting server on http://0.0.0.0:8081
You can access the application at:
  - Local: http://localhost:8081
  - Network: http://192.168.1.100:8081 (for other computers on the same network)
  - For remote access, deploy to a cloud hosting service.
  - See README.md for deployment instructions.
===============================
```

Note: The application uses HTTP by default. The server will display these addresses when you start it.

#### Same Network Access

For a presentation or demonstration on the same network:
1. Make sure all computers are connected to the same network (WiFi or LAN)
2. Run the application on your computer using `python run.py`
3. Share the "Network" URL with others so they can access the chatbot from their browsers

#### Remote Access (from any network)

For remote access, we recommend using Render.com:

##### Render.com (Free Hosting)

Render.com is a cloud platform that allows you to deploy Python web applications for free. This is the recommended option for remote access and long-term hosting.

See the [Deploying to Render.com](#option-1-deploy-to-rendercom-recommended) section below for detailed instructions.

### Troubleshooting Network Access

#### Same Network Access Issues

If other computers on the same network cannot access your application:

1. **Firewall Settings**: Make sure your firewall allows incoming connections on the port you're using (default: 8081)
   - Windows: Check Windows Defender Firewall settings
   - macOS: Check System Preferences > Security & Privacy > Firewall
   - Linux: Check your distribution's firewall settings (e.g., `ufw status` on Ubuntu)

2. **Network Restrictions**: Some networks (especially in schools or public places) may block direct connections between computers
   - Try using a mobile hotspot if available
   - Ask your network administrator if there are any restrictions

3. **Correct IP Address**: Make sure you're using the correct network IP address
   - If your computer has multiple network adapters (e.g., Ethernet and WiFi), the displayed IP might not be the one you need
   - You can check all your IP addresses by running:
     - Windows: `ipconfig` in Command Prompt
     - macOS/Linux: `ifconfig` or `ip addr` in Terminal

#### Remote Access Issues

##### Render.com Issues

If you're having trouble with Render.com deployment:

1. **Configuration**: Make sure your render.yaml configuration file is correct
   - Check the logs in the Render.com dashboard
   - Verify that the paths in your configuration match your actual file structure

2. **Dependencies**: Ensure all required packages are installed
   - Check the build logs to see if all dependencies were installed correctly
   - Make sure you're using a compatible Python version

3. **Database Setup**: Verify your database configuration
   - Update your environment variables to use the correct database URL
   - Run database migrations if needed

4. **Static Files**: If static files (CSS, JS, images) aren't loading
   - Make sure the URLs in your templates are correct
   - Check that your static files are being served correctly


## Deployment

This project can be deployed to various cloud platforms. We provide deployment scripts and instructions for Render.com, a recommended free hosting option.

### Deploy to Render.com

The easiest way to deploy is using our new Render.com deployment script:

1. Make the script executable:
   ```bash
   chmod +x deploy_to_render.sh
   ```

2. Run the script:
   ```bash
   ./deploy_to_render.sh
   ```

3. The script will guide you through:
   - Creating a Render.com account (free tier available)
   - Connecting your GitHub repository
   - Deploying using Render's Blueprint feature
   - Monitoring the deployment process
   - Accessing your deployed application

4. Your app will be available at the URL provided by Render (e.g., `https://emotion-aware-chatbot.onrender.com`)

5. To verify your deployment, run the test script:
   ```bash
   # Make the script executable first (if not already)
   chmod +x test_render_deployment.py

   # Run the test script
   ./test_render_deployment.py <your-render-url>

   # Or alternatively
   python test_render_deployment.py <your-render-url>
   ```
   This script will check if your application is running correctly and test basic functionality.

6. **Benefits of Render.com:**
   - Free tier available
   - Automatic HTTPS
   - Easy deployment from GitHub
   - No need for manual server configuration
   - Persistent disk storage for your database


## Testing Emotions

### Basic Emotion Examples

Here are some example prompts to test different explicit emotions:

- Joy: "I'm so happy! I just got promoted at work!"
- Sadness: "I feel really down today, everything seems hopeless"
- Anger: "I'm absolutely furious about what happened!"
- Fear: "I'm really scared about the upcoming presentation"
- Surprise: "Wow! I never expected that to happen!"
- Trust: "I completely believe in what you're saying"
- Grief: "I miss my loved one so much, it hurts"
- Relief: "Thank goodness that's over, I was so worried"
- Panic: "Oh no! I don't know what to do!"
- Disgust: "That's absolutely revolting, I can't stand it"

### Real-Life Text Examples

The chatbot can now detect emotions in more nuanced, real-life texts:

- Mixed emotions: "I was excited about the trip, but now I'm worried about the cost."
- Implicit emotions: "I just got back from the interview. They said they'll let me know next week."
- Subtle emotions: "I guess we could try that approach. It might work."
- Negation handling: "I'm not upset, just a bit tired from all the work."
- Context-dependent: "The presentation went well, but I'm not sure if they understood all the key points."
- Real-life situations: "My car broke down on the way to the important meeting. Had to call a taxi."

## Project Structure

```
chatbot_app/
├── __init__.py         # Application factory
├── __main__.py         # Entry point when run as a module
├── config.py           # Configuration settings
├── error_handlers.py   # Error handlers
├── models.py           # Database models
├── routes/             # Route blueprints
│   ├── __init__.py
│   └── main.py         # Main routes
├── chatbot/            # Chatbot functionality
│   ├── __init__.py
│   ├── advanced_chatbot.py
│   ├── detect_implicit_emotions.py
│   └── drinks_recommendations.py
├── static/             # Static files
│   ├── alcohol/        # Drink images
│   ├── images/         # Emotion images
│   └── favicon.ico
└── templates/          # HTML templates
    ├── german_chatbot/
    ├── index.html      # Main chat interface
    └── nlp_mining/

tests/                  # Test suite (in chatbot_app/tests/)
├── __init__.py
├── conftest.py         # Test fixtures
└── chatbot/            # Chatbot tests
    └── __init__.py
```

### Core Files
- `run.py`: Script to run the application
- `setup.py`: Package installation script
- `requirements.txt`: Project dependencies
- `MANIFEST.in`: Package manifest file

### Deployment Files
- `deploy_to_render.sh`: Script for deploying to Render.com
- `test_render_deployment.py`: Script for testing Render.com deployment
- `test_deployment.py`: General deployment testing script

### Documentation
- `README.md`: This file - main documentation

## Contributing

Feel free to submit issues and enhancement requests!

## Color Scheme

The application uses a carefully chosen dark purple color palette for optimal readability and aesthetic appeal:

```css
--bg-primary: #13111C     /* Deep purple background */
--bg-secondary: #1E1B2E   /* Secondary purple background */
--text-primary: #E9E8FF   /* Bright purple text */
--text-secondary: #B4B2C5 /* Muted purple text */
--accent-primary: #9333EA /* Vibrant purple accent */
--accent-hover: #A855F7   /* Light purple hover state */
--gradient-start: #9333EA /* Gradient start color */
--gradient-end: #7C3AED   /* Gradient end color */
--success: #059669        /* Success state color */
--error: #EF4444         /* Error state color */
--border: #2D2B3D        /* Dark purple border */
```

## Visual Features

- Gradient backgrounds and accents
- Smooth hover animations
- Image display for each emotion
- Responsive image layout
- Interactive UI elements
- Loading states and transitions

## Technical Details

### Frontend

- Modern HTML5 and CSS3
- Responsive design using CSS Grid and Flexbox
- Dark mode optimized for reduced eye strain
- Interactive elements with hover states
- Smooth transitions and animations
- Error handling and loading states

### Backend

- Flask web framework
- Advanced NLP techniques for emotion detection:
  - Sentence-level context analysis for multi-sentence messages
  - Negation handling for complex sentiment expressions
  - Implicit emotion detection from linguistic patterns
  - Context window analysis for related words and phrases
  - Temporal and structural analysis of message content
- Pattern recognition for complex emotional states
- Enhanced detection of mixed and subtle emotions
- Emotional continuity tracking across conversations
- SQLite database for storing analysis history

## Troubleshooting

### Port Conflicts

If you encounter an error message like "address is already in use" when starting the application, it means the default port (8081) is already being used by another program on your system. You can resolve this by:

1. Specifying a different port in your `.env` file:
   ```
   PORT=5000  # Or any other available port
   ```

2. Stopping the other application that's using the port

3. Using an environment variable when running the application:
   ```bash
   PORT=5000 python run.py
   ```

## Development

### Python Interpreter Setup

This project is compatible with Python 3.12.3 and Python 3.13. A virtual environment is already set up in the `venv` directory with all required dependencies installed.

#### PyCharm Configuration
If you're using PyCharm:
1. Go to File > Settings > Project > Python Interpreter
2. Click on the gear icon and select "Add..."
3. Choose "Existing Environment" 
4. Browse to `/home/admin123/PycharmProjects/DjangoProject/venv/bin/python`
5. Click "OK" to save the configuration

#### Manual Setup
If you're not using PyCharm:
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Run the application:
   ```bash
   python run.py
   ```

### Running Tests

```bash
pytest
```

Or with coverage:

```bash
python run_tests_with_coverage.py
```

### Development Workflow

1. Make changes to the code
2. Run tests to ensure functionality
3. Update documentation if necessary
4. Submit a pull request

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Hugging Face for the transformer models
- Flask team for the web framework
- Contributors and maintainers
