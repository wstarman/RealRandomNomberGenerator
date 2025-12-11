# AudioRNG – Software Requirements Specification

## Software Requirements Specification for an Audio-Based Random Number Generator

Contributions:

| Student ID | Name | Works |  |  | Contribution |
| :---- | :---- | :---- | ----- | ----- | :---- |
| B11215003 | 吳柏潁 | Documentations, UML Diagrams, Frontend Interfaces, \*Presentation, Research Data Collection |  |  | 50% |
| B11215023 | 裘承軒 | Documentations, UML Diagrams, Frontend Interfaces |  |  | 19% |
| B11215059 | 翁世承 | Documentation, UML Diagrams, AudioRNGLib Library, Prototyping |  |  | 12% |
| B11215001 | 陳鴻量 | Documentations, UML Diagrams, Backend Service  |  |  | 19% |

# Section 1: Introduction

## 1.1 Purpose

This document specifies the software requirements for AudioRNG, a True Random Number Generator (TRNG) system that utilizes environmental audio captured from a USB microphone as an entropy source. The system provides random number generation services through both programmatic APIs and web-based user interfaces, offering an accessible alternative to hardware random number generators.  
This SRS document is intended for:

* All team members requiring a unified understanding of system requirements and architecture  
* Backend developers implementing the AudioRNGLib library and REST API server  
* Frontend developers creating the web user interfaces  
* Quality assurance personnel conducting system testing and validation  
* Course instructors and teaching assistants evaluating the project  
* Future developers who may extend or maintain the system

This SRS serves as the definitive reference for functional requirements, system constraints, interface specifications, and design decisions throughout the development lifecycle.

## 1.2 Product Scope

The system encompasses three primary components:

* Web Frontend: Two user interfaces for different interaction models  
* Backend Server: A RESTful API service that utilizes AudioRNGLib  
* AudioRNGLib: A Python library for audio-based entropy collection and random number generation using PyAudio

### What the System WILL Provide

* Server-side random number generation using audio entropy  
* REST API for programmatic access  
* Web-based basic random number generator interface  
* Web-based lottery picker interface with animated wheel  
* Automatic fallback to pseudo-random when microphone unavailable  
* Entropy source transparency (indicates true random vs. pseudo-random)

### What the System will NOT Provide

* Browser-based microphone capture (server-side only)  
* Public package distribution  
* Persistent storage or logging  
* Audio recording or playback  
* Cryptographic key management  
* Mobile-responsive interfaces  
* Multiple microphone device selection

### Benefits and Objectives

* Accessibility: Uses inexpensive USB microphones instead of specialized hardware  
* Physical Entropy: Leverages unpredictable environmental audio  
* Modularity: Clean separation between library, backend, and frontend  
* Extensibility: Dual-interface design shows multiple use cases from single backend

## 1.3 Intended Audience and Use

AudioRNG is designed for 2 user classes:

### User Class 1: End Users (General Public)

For the general public, AudioRNG provides applications requiring random selections, such as lottery draws, random team assignments, and game mechanics through its extensible web interfaces.

* Experience: First-time users should understand system without training  
* Environment: Windows PC with modern browser  
* Primary Tasks:  
  * Generate random numbers for general purposes  
  * Use lottery picker for fair selection  
* Needs: Simple interface with clear visual feedback

### User Class 2: API Consumers (Developers)

For developers, AudioRNG provides random numbers for software testing, simulations, and development environments where true randomness improves test coverage. AudioRNG also offers a transparent, auditable source of randomness for research requiring documented random number generation

* Experience: Familiar with REST APIs and JSON  
* Primary Tasks:  
  * Integrate AudioRNG into other projects  
  * Retrieve random numbers programmatically  
* Needs: Simple, well-documented API with predictable responses

## 1.4 Definitions and Acronyms

### Acronyms

* API: Application Programming Interface  
* REST: Representational State Transfer  
* RNG: Random Number Generator  
* TRNG: True Random Number Generator  
* USB: Universal Serial Bus  
* PCM: Pulse-Code Modulation  
* SVG: Scalable Vector Graphics

### Definitions

* AudioRNGLib: Core Python library handling audio capture and random number generation  
* Entropy: Measure of randomness collected from physical sources  
* Microphone Mode: Operating mode using true random entropy from audio  
* Fallback Mode: Operating mode using pseudo-random generation

## 1.5 References

1. Next.js Documentation: Vercel Inc., Available: https://nextjs.org/docs  
2. Mantine UI Documentation: Available: https://mantine.dev/  
3. FastAPI Documentation: Available: https://fastapi.tiangolo.com/  
4. PyAudio Documentation: Available: https://people.csail.mit.edu/hubert/pyaudio/

# Section 2: General Description

## 2.1 System Boundary

AudioRNG is an independent, self-contained application for local development. The USB microphone is external hardware. The system encompasses AudioRNGLib, backend API, and frontend as internal components. Operating system drivers, browsers, and runtimes are external dependencies.

### System Architecture

![][image1]  
The system uses three-tier architecture:

* Frontend Layer: Two web interfaces (WebUI and Wheel Lottery Web APP) communicate with backend via HTTP REST API  
* Backend Layer: API server integrates with AudioRNGLib for random number generation  
* Library Layer: Python module interfaces with OS audio subsystem, processes audio input or provides fallback  
* External Dependencies: USB microphone, Windows audio drivers, web browser, Python and Node.js runtimes  
* Deployment: Local development on Windows machines via localhost only

## 2.2 Product Functions

The AudioRNG system provides the following major functions:

### F1: Audio-Based Entropy Collection

* Capture audio frames from USB microphone using PyAudio  
* Process audio data through SHA-256 hashing  
* Convert hash output to normalized floating-point number (0.0 to 1.0)  
* Automatically detect microphone and fall back to pseudo-random if unavailable  
* Track and report entropy source (microphone or fallback)

### F2: Random Number Generation API

* Expose RESTful API endpoint for random number requests  
* Return random number with source metadata and timestamp in JSON  
* Handle errors with appropriate HTTP status codes

### F3: Basic Random Number Generation Interface

* Display random numbers from backend  
* Show entropy source via color-coded indicator  
* Request new random numbers on-demand  
* Display response metadata (timestamp, source)  
* Show loading state during API calls

### F4: Lottery Wheel Picker Interface

* Accept user-defined options via interactive controls  
* Display options on animated spinning wheel  
* Use backend random number to select winning option  
* Animate wheel spin based on random value  
* Display winning selection via browser alert  
* Show entropy source via color-coded indicator

### F5: Source Transparency

* Indicate whether using microphone (true random) or fallback (pseudo-random)  
* Provide visual feedback through color-coded status indicators  
* Include source information in API responses

## 2.3 System Internal Interfaces

The AudioRNG system has the following internal system interfaces:

### Library-to-Backend Interface

* Interface Type: Direct function calls (Python module import)  
* Functions Exposed:  
  * float getRand(): Returns a random floating-point number between 0.0 and 1.0 (inclusive)  
  * string getSource(): Returns entropy source indicator, either "microphone" or "fallback"  
* Communication Method: Synchronous function calls within the same Python process  
* Error Handling Strategy: The library uses exception-based error handling to maintain simplicity:  
  * MicrophoneNotFoundError: Raised when no audio input device is detected during initialization  
  * AudioCaptureError: Raised when PyAudio fails to capture audio frames  
  * HashingError: Raised if SHA-256 hashing operation fails (unlikely but handled for completeness)  
* When an exception is raised, the library automatically attempts to fall back to the Python random module and updates the source state to "fallback". If fallback also fails (extremely rare), the exception propagates to the caller (backend server).

### Backend-to-Frontend Interface

* Interface Type: RESTful HTTP API  
* Endpoint: GET /api/random  
* Request Parameters: None  
* Response Format: JSON  
* Example Response :  
  * Status Code: 200 OK  
  * Response Body: {"rand": 0.123456789,  "source": "microphone",  "timestamp": "2025-10-28T14:30:00Z"}  
* Response Fields:  
  * rand (float): Random number between 0.0 and 1.0  
  * source (string): Either "microphone" or "fallback"  
  * timestamp (string): ISO 8601 format timestamp  
* Example Error Response :  
  * Status Code: 500 Internal Server Error  
  * Response Body: {"error": "Internal server error"}  
* Error Response Fields:  
  * error (string): Describe the error to the end users  
* CORS: Not enabled (local-only deployment, no cross-origin requests)

## 2.4 System External Interfaces

### 2.4.1 User Interfaces

The system provides two distinct web-based user interfaces optimized for desktop browsers:

#### Basic Random Number Generator Interface:

* Layout:  
  1. Page title displayed at the top  
  2. Display area showing the generated random number prominently  
  3. Display area showing source ("microphone" or "fallback") and timestamp  
  4. Action button to generate new random number  
  5. Status indicator in corner (green for microphone, red for fallback)  
* Interaction Flow:  
  1. User clicks the generate button  
  2. System displays loading state  
  3. System calls backend API  
  4. Display updates with new random number and metadata  
  5. Status indicator reflects current entropy source  
* Error Handling: Browser alert displays error message if API call fails

#### Lottery Picker Interface:

* Layout:  
  * Page title at the top center  
  * Two control buttons in top-right corner: "Start/Spin" button (primary color) and "Reset" button (secondary color)  
  * Large interactive wheel display on the left side showing all available options as colored segments with a fixed pointer  
  * Right-side control panel containing:  
    * Scrollable list showing all items currently in the wheel  
    * Management buttons below the list for editing items  
  * Status indicator in corner (green for microphone, red for fallback)  
* Interaction Flow:  
  * User adds items to the wheel (items appear in both wheel and list)  
  * User can edit or remove items using the management buttons  
  * User clicks "Start/Spin" button to begin selection  
  * System displays loading state while requesting random number  
  * Wheel animates spinning and gradually slows down  
  * Wheel stops at selected option based on random number  
  * Browser alert displays the winning selection  
* Wheel Behavior:  
  * Minimum 1 item required to spin  
  * Wheel segments automatically adjust size based on number of items  
  * Each item shown as a colored segment with visible label  
  * Fixed pointer indicates the winning position  
* Error Handling: Browser alert displays error message if API call fails

#### Common Elements:

* Status Indicator: Small colored circle (green \= microphone, red \= fallback)  
* Loading State: Semi-transparent overlay with spinner during API calls  
* Error Display: Browser native alert for error messages  
* API Client

### 2.4.2 Hardware Interfaces

#### USB Microphone Interface:

* Device Type: Standard USB audio input device  
* Connection: USB compatible port  
* Supported Devices: USB Audio Device Class compliant microphones  
* Audio Format: PyAudio default settings (typically 16-bit PCM, 44.1 kHz)  
* Buffer Size: PyAudio default settings  
* Interface Library: PyAudio as abstraction layer for Windows audio drivers  
* Device Selection: System default audio input device  
* Fallback Behavior: If no microphone detected, automatically switch to Python random module  
* Platform Support: Windows via PyAudio

### 2.4.3 Software Interfaces

#### AudioRNGLib Dependencies:

* PyAudio  
  * Purpose: Capture audio frames from USB microphone  
  * Version: Latest stable version from PyPI (0.2.14 or newer)  
  * Source: PyPI (Python Package Index)  
  * Interface: Python API for audio input/output  
  * Note: Requires PortAudio C library (bundled with PyAudio wheel on Windows)  
* hashlib (SHA-256)  
  * Purpose: Hash audio data to generate random numbers  
  * Version: Python standard library (included with Python 3.14)  
  * Source: Python standard library  
  * Interface: hashlib.sha256() for cryptographic hashing  
* Python random module  
  * Purpose: Fallback entropy source when microphone unavailable  
  * Version: Python standard library (included with Python 3.14)  
  * Source: Python standard library  
  * Interface: random.random() for pseudo-random generation

#### Backend Server Dependencies:

* FastAPI  
  * Purpose: HTTP request handling and routing  
  * Version: 0.120.x (latest in 0.120 series)  
  * Source: PyPI  
  * Interface: Decorator-based routing  
* Uvicorn  
  * Purpose: ASGI server for FastAPI  
  * Version: Compatible with FastAPI 0.120.x  
  * Source: PyPI  
* Python Runtime  
  * Version: Python 3.14  
  * Source: python.org  
  * Platform: Windows  
* AudioRNGLib  
  * Purpose: Generate random numbers  
  * Version: 1.0.0 (internal library)  
  * Source: Internal to project  
  * Interface: getRand() and getSource() functions

#### Frontend Dependencies:

* Next.js  
  * Purpose: React framework for building static web application  
  * Version: 16.0.x  
  * Source: npm  
  * Configuration: Pages Router with Static Export (SSG)  
* Mantine UI  
  * Purpose: React component library  
  * Version: 8.3.x  
  * Source: npm  
* Node.js  
  * Purpose: Build tooling for frontend  
  * Version: 24.x (LTS)  
  * Source: nodejs.org  
* Browser Requirements:  
  * Chrome 90+, Firefox 88+, or Edge 90+ on Windows  
  * JavaScript must be enabled

### 2.4.4 Communications Interfaces

HTTP Protocol:

* Protocol: HTTP/1.1 (no HTTPS required for localhost)  
* Port: 8000  
* Server Address: http://localhost:8000  
* Request Method: GET  
* Endpoint: /api/random  
* Content-Type: application/json (response)  
* Character Encoding: UTF-8

Network Requirements:

* Bandwidth: Minimal (each response approximately 100-200 bytes)  
* Connection Type: Stateless HTTP requests  
* Deployment: Local network only (localhost loopback)

Security:

* No HTTPS required (local deployment only)  
* No authentication or authorization (open API on localhost)

### 2.5 Operations

Development Mode (Only Operational Mode):

* Backend runs locally at http://localhost:8000  
* Frontend runs on Next.js development server at http://localhost:3000  
* Audio capture occurs on-demand when getRand() is called  
* No scheduled maintenance operations required

Startup Sequence:

* Backend:  
  1. Install Python 3.14 and dependencies via pip  
  2. Navigate to backend directory  
  3. Run: uvicorn main:app \--reload \--port 8000  
* Frontend:  
  1. Install Node.js 24.x and dependencies via npm  
  2. Navigate to frontend directory  
  3. Run: npm run dev  
* Shutdown: Ctrl+C in respective terminals

Error Recovery:

* No data persistence required (stateless application)  
* Recovery: Restart the affected component (backend or frontend)  
* Microphone errors: System automatically falls back to pseudo-random

# Section 3: Specific Requirements

## 3.1 External Interface Requirements

### 3.1.1 User Interfaces

UI-001: Basic Random Number Generator Interface

* UI-001.1: The interface shall display the random number, entropy source, and timestamp  
* UI-001.2: The interface shall provide a "Pick a Number" button to trigger generation  
* UI-001.3: The interface shall display a status indicator showing green for microphone mode and red for fallback mode  
* UI-001.4: The interface shall display a loading overlay during API requests  
* UI-001.5: The interface shall display error messages via browser alert when requests fail

UI-002: Lottery Picker Interface

* UI-002.1: The interface shall display an interactive wheel visualization with user-defined items  
* UI-002.2: The interface shall provide text input and "Add" button for adding items to the wheel  
* UI-002.3: The interface shall display a list of added items with "Edit" and "Delete" buttons  
* UI-002.4: The interface shall provide a "Spin" button to trigger wheel animation  
* UI-002.5: The interface shall animate the wheel for exactly 3.0 seconds using SVG and CSS  
* UI-002.6: The interface shall use 6 colors (red, blue, green, yellow, purple, orange) for wheel segments  
* UI-002.7: The interface shall display the winning selection via UI popup  
* UI-002.8: The interface shall display status indicator and loading states like the basic interface

### 3.1.2 Hardware Interfaces

HW-001: Audio Input Device Interface

* HW-001.1: AudioRNGLib shall capture audio at 44,100 Hz sample rate, 16-bit PCM, mono channel  
* HW-001.2: AudioRNGLib shall use buffer size of 1024 samples  
* HW-001.3: AudioRNGLib shall use the Windows default audio input device  
* HW-001.4: AudioRNGLib shall support any USB Audio Device Class compliant microphone  
* HW-001.5: AudioRNGLib shall automatically fall back to pseudo-random mode if no microphone detected  
* HW-001.6: AudioRNGLib shall close audio streams immediately after capture and not store audio data

### 3.1.3 Software Interfaces

SW-001: Core Dependencies

* SW-001.1: AudioRNGLib shall use PyAudio version 0.2.14 or newer for audio capture  
* SW-001.2: AudioRNGLib shall use Python's hashlib.sha256() for hashing  
* SW-001.3: AudioRNGLib shall use Python's random.random() for fallback mode  
* SW-001.4: Backend shall use FastAPI version 0.120.x with Uvicorn ASGI server  
* SW-001.5: Frontend shall use Next.js version 16.0.x with Mantine UI version 8.3.x  
* SW-001.6: Frontend shall use Node.js version 24.x for build tooling

SW-002: Browser Requirements

* SW-002.1: Frontend shall support Chrome 90+, Firefox 88+, Edge 90+ on Windows  
* SW-002.2: Frontend shall require JavaScript enabled

### 3.1.4 Communications Interfaces

COMM-001: HTTP API

* COMM-001.1: Backend shall expose endpoint GET /api/random on localhost:8000  
* COMM-001.2: Endpoint shall return JSON with three fields: "rand" (float 0.0-1.0), "source" (string: "microphone" or "fallback"), "timestamp" (ISO 8601 format)  
* COMM-001.3: Endpoint shall return HTTP 200 for success, HTTP 500 for errors  
* COMM-001.4: Endpoint shall not require HTTPS, CORS, authentication, or session management

## 3.2 Functional Requirements

### 3.2.1 Audio-Based Entropy Collection

FR-001: Audio Capture and Processing

* FR-001.1: AudioRNGLib shall detect available audio devices during initialization  
* FR-001.2: AudioRNGLib shall capture 1024 samples (2048 bytes) of audio when getRand() is called  
* FR-001.3: AudioRNGLib shall hash the raw audio bytes using SHA-256  
* FR-001.4: AudioRNGLib shall convert the first 8 bytes of hash to float in range \[0.0, 1.0\]  
* FR-001.5: AudioRNGLib shall discard audio data immediately after hashing  
* FR-001.6: AudioRNGLib shall use Python's random.random() if microphone unavailable  
* FR-001.7: AudioRNGLib shall process fallback values through SHA-256 for consistency

FR-002: Entropy Source Management

* FR-002.1: AudioRNGLib shall expose getSource() function returning "microphone" or "fallback"  
* FR-002.2: AudioRNGLib shall automatically transition to fallback mode when audio capture fails  
* FR-002.3: AudioRNGLib shall attempt to use microphone on next call after reconnection

FR-003: Error Handling

* FR-003.1: AudioRNGLib shall raise MicrophoneNotFoundError when no device detected  
* FR-003.2: AudioRNGLib shall raise AudioCaptureError when PyAudio fails  
* FR-003.3: AudioRNGLib shall attempt fallback after exceptions  
* FR-003.4: AudioRNGLib shall not crash or hang when errors occur

### 3.2.2 Random Number Generation API

FR-004: API Endpoint

* FR-004.1: Backend shall expose GET /api/random endpoint  
* FR-004.2: Endpoint shall call AudioRNGLib.getRand() and getSource()  
* FR-004.3: Endpoint shall generate ISO 8601 timestamp for each response  
* FR-004.4: Endpoint shall construct JSON response with rand, source, and timestamp  
* FR-004.5: Endpoint shall return HTTP 200 with JSON on success  
* FR-004.6: Endpoint shall return HTTP 500 with generic error message on failure  
* FR-004.7: Endpoint shall log detailed errors to server console (not expose to client)  
* FR-004.8: Endpoint shall timeout after 5 seconds

### 3.2.3 Basic Random Number Generator Interface

FR-005: Display and Interaction

* FR-005.1: Interface shall display rand, source, and timestamp from API responses  
* FR-005.2: Interface shall set status indicator to green when source is "microphone"  
* FR-005.3: Interface shall set status indicator to red when source is "fallback"  
* FR-005.4: Interface shall send GET request to /api/random when user clicks generate button  
* FR-005.5: Interface shall display loading overlay during API requests  
* FR-005.6: Interface shall update display within 100ms of receiving API response  
* FR-005.7: Interface shall display error alert when API request fails

### 3.2.4 Lottery Picker Interface

FR-006: Item Management and Wheel Animation

* FR-006.1: Interface shall accept user input to add items (max 100 characters each, max 1000 items total)  
* FR-006.2: Interface shall allow editing and deleting items  
* FR-006.3: Interface shall update wheel visualization when items change  
* FR-006.4: Interface shall send GET request to /api/random when user clicks spin button  
* FR-006.5: Interface shall map random number to wheel segment  
* FR-006.6: Interface shall animate wheel rotation for exactly 3.0 seconds using CSS  
* FR-006.7: Interface shall display winning selection in UI popup  
* FR-006.8: Interface shall display status indicator showing entropy source

## 3.3 Non-Functional Requirements

### 3.3.1 Security Requirements

* SEC-001: Input Validation and Privacy  
  * SEC-001.1: Frontend shall reject lottery items exceeding 100 characters  
  * SEC-001.2: Frontend shall sanitize user inputs to prevent XSS attacks  
  * SEC-001.3: Backend shall not expose stack traces, file paths, or internal details in API responses  
  * SEC-001.4: Backend shall log detailed errors to console only (not to clients)  
  * SEC-001.5: System shall not collect, store, or log user data or generated values  
  * SEC-001.6: Audio data shall be processed in-memory only and discarded after hashing  
* SEC-002: Data Storage  
  * SEC-002.1: System shall not implement persistent data storage  
  * SEC-002.2: Random numbers shall be discarded after API response  
  * SEC-002.3: Audio data shall be discarded immediately after hashing  
  * SEC-002.4: Lottery items shall persist only during browser session  
* SEC-003: Data Integrity  
  * SEC-003.1: Random numbers shall always be in range \[0.0, 1.0\]  
  * SEC-003.2: Source indicator shall only be "microphone" or "fallback"  
  * SEC-003.3: Timestamps shall conform to ISO 8601 format

### 3.3.2 Capacity Requirements

* CAP-001: Performance Limits  
  * CAP-001.1: System shall respond to API requests within 500ms under normal conditions  
  * CAP-001.2: Backend shall handle at least 10 sequential requests without degradation  
  * CAP-001.3: Lottery picker shall support a maximum of 1000 items  
* CAP-002: Resource Constraints  
  * CAP-002.1: AudioRNGLib shall capture audio frames using default PyAudio buffer size  
  * CAP-002.2: Backend server shall operate within 100MB of memory usage under normal load  
  * CAP-002.3: Frontend interfaces shall load completely within 3 seconds on modern browsers

### 3.3.3 Compatibility Requirements

* COMP-001: Development Environment  
  * COMP-001.1: Backend requires Python 3.14 with pip on Windows  
  * COMP-001.2: Frontend requires Node.js 24.x with npm on Windows  
  * COMP-001.3: requirements.txt shall list all Python dependencies  
  * COMP-001.4: package.json shall list all Node.js dependencies  
  * COMP-001.5: Backend shall run with: uvicorn main:app \--reload \--port 8000  
  * COMP-001.6: Frontend shall run with: npm run dev

### 3.3.4 Reliability Requirements

* REL-001: Fault Tolerance  
  * REL-001.1: System shall automatically fall back to pseudo-random when microphone fails  
  * REL-001.2: System shall indicate current entropy source in all responses  
  * REL-001.3: Errors shall not crash browser application or server process  
  * REL-001.4: System shall recover from transient errors without user intervention

### 3.3.5 Scalability Requirements

* SCAL-001: Current Scope Limitations  
  * SCAL-001.1: System is designed for single-user, local deployment only  
  * SCAL-001.2: System is not required to handle concurrent users or distributed deployment  
  * SCAL-001.3: System is not required to support horizontal or vertical scaling  
* SCAL-002: Future Considerations  
  * SCAL-002.1: Code architecture shall maintain separation of concerns to facilitate future scaling if needed  
  * SCAL-002.2: API design shall follow REST principles to support potential future enhancements

### 3.3.6 Maintainability Requirements

* MAINT-001: Code Organization and Documentation  
  * MAINT-001.1: AudioRNGLib shall be a separate Python module  
  * MAINT-001.2: Frontend shall use component-based architecture  
  * MAINT-001.3: All public functions shall include docstrings  
  * MAINT-001.4: Complex logic shall include inline comments  
  * MAINT-001.5: Components shall be testable independently

### 3.3.7 Usability Requirements

* USA-001: Ease of Use  
  * USA-001.1: First-time users shall be able to generate a random number without instructions  
  * USA-001.2: Lottery picker shall allow adding items within 2 clicks  
  * USA-001.3: All interactive elements shall provide visual feedback on hover or click  
* USA-002: Visual Feedback and Clarity  
  * USA-002.1: Status indicator shall be clearly visible with color-coded states (green/red)  
  * USA-002.2: Loading states shall be displayed during all API operations  
  * USA-002.3: Error messages shall be displayed in clear, user-friendly language  
  * USA-002.4: Generated random numbers shall be displayed in large, readable font  
* USA-003: Documentation and Learnability  
  * USA-003.1: API documentation shall include example requests and responses  
  * USA-003.2: Interface labels and buttons shall use clear, descriptive text  
  * USA-003.3: Lottery wheel animation shall complete within 3 seconds for optimal user experience

### 3.3.8 Other Requirements

#### 3.3.8.1 Design Constraints

* DC-001: Technology Stack  
  * DC-001.1: Backend and library shall be implemented in Python 3.14  
  * DC-001.2: Frontend shall be implemented using Next.js 16.0.x with TypeScript/JavaScript  
  * DC-001.3: Backend shall use FastAPI 0.120.x framework  
  * DC-001.4: Frontend shall use Mantine UI 8.3.x for components  
  * DC-001.5: Audio capture shall use PyAudio library  
  * DC-001.6: Hashing shall use SHA-256 from Python's hashlib  
  * DC-001.7: Wheel visualization shall use SVG with CSS transitions  
* DC-002: Platform Constraints  
  * DC-002.1: System shall be developed and tested on Windows  
  * DC-002.2: Backend and frontend shall run on localhost only  
  * DC-002.3: Backend shall use TCP port 8000, frontend shall use port 3000  
* DC-003: Architecture Constraints  
  * DC-003.1: System shall use stateless RESTful HTTP API  
  * DC-003.2: System shall not implement authentication, sessions, or persistent storage  
  * DC-003.3: Frontend shall communicate via HTTP GET requests only  
* DC-004: Project Constraints  
  * DC-004.1: Project shall be completed within one month  
  * DC-004.2: Development team shall consist of four developers  
  * DC-004.3: All tools and libraries shall be free and open-source

#### 3.3.8.2 Testing Requirements

* TEST-001: Testing Strategy  
  * TEST-001.1: AudioRNGLib functions shall have unit tests  
  * TEST-001.2: Backend API shall have integration tests verifying JSON format  
  * TEST-001.3: End-to-end test shall verify frontend → backend → display flow  
  * TEST-001.4: Manual testing shall verify both microphone and fallback modes  
  * TEST-001.5: Manual testing shall verify status indicators correctly show entropy source

#### 3.3.8.3 Demonstration Requirements

* DEMO-001: Demonstration Setup  
  * DEMO-001.1: System shall demonstrate microphone mode with USB microphone connected  
  * DEMO-001.2: System shall demonstrate fallback mode with microphone disconnected  
  * DEMO-001.3: Lottery wheel shall be pre-loaded with 8-10 example items  
  * DEMO-001.4: Demonstration shall show multiple spins producing different winners  
  * DEMO-001.5: Demonstration shall highlight automatic fallback mechanism

#### 3.3.8.4 Preliminary Validation

Purpose:  
Prior to full system implementation, preliminary validation was conducted to verify the feasibility and effectiveness of the core entropy generation concept. This early-stage testing demonstrates that the approach of transforming audio input through cryptographic hashing produces statistically uniform random numbers.

* VAL-001: Validation Methodology  
  * VAL-001.1: A test script (test\_randomness.py) generated 10,000 random numbers for analysis  
  * VAL-001.2: Random numbers were collected in microphone mode to validate audio entropy  
  * VAL-001.3: Values were binned into 50 equal-width bins spanning \[0.0, 1.0\]  
  * VAL-001.4: Distributions were visualized as histograms for inspection  
* VAL-002: Validation Results  
  * VAL-002.1: Raw Audio Distribution: Microphone amplitude samples exhibited normal (Gaussian) distribution centered at zero, confirming typical environmental audio characteristics  
  * VAL-002.2: Hashed Output Distribution: SHA-256 hashed outputs exhibited uniform distribution across \[0.0, 1.0\] with approximately 1500 samples per bin, demonstrating successful transformation  
  * VAL-002.3: Key Finding: The transformation from normal distribution (raw audio) to uniform distribution (hashed output) validates that SHA-256 cryptographic hashing converts physical audio entropy into high-quality random numbers  
* VAL-003: Implications  
  * VAL-003.1: Preliminary results demonstrate feasibility of the audio-to-randomness approach  
  * VAL-003.2: Uniform distribution supports the decision to use SHA-256 hashing  
  * VAL-003.3: The test methodology (test\_randomness.py) provides validation approach for final system  
  * VAL-003.4: Visual histogram inspection is sufficient for quality validation in this educational project

# Appendix

## 1\. Sequence UML

![][image2]

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>