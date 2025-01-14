# LiveResume
#### _Your Resume on GitHub Pages_

Transform your resume into a professional online presence that's always accessible and looks great on any device.

## Built with AI in 24 Hours

This project demonstrates the practical application of AI-assisted development. Created in 24 hours using AI pair programming.

## Key Features

- **Quick Setup**: Convert your existing resume to a professional website in minutes
- **Format Flexibility**: 
  - Support for PDF, Word, and Markdown formats
  - Clean conversion with preserved formatting
- **AI Enhancement**: 
  - Content improvement suggestions
  - Formatting optimization
- **Professional Themes**: 
  - Basic: Clean and minimal design
  - Modern: Contemporary and sophisticated layout
  - Terminal: Tech-inspired theme
- **Version Control**: 
  - Powered by GitHub Pages
  - Easy updates and maintenance

## Prerequisites

- Python 3.10+
- Flask
- GitHub account (for saving and sharing features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hitheshaum/live-resume.git
cd live-resume
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_CLIENT_ID=your_github_oauth_app_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_app_client_secret
```

To get these credentials:
- Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with `public_repo` scope. This is primarily used for using 'Github Models'
- Register a [GitHub OAuth Application](https://github.com/settings/developers) and get the Client ID and Secret. Use http://localhost:5000 as the callback URL and website URL. This is used for GitHub authentication.

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Login with your GitHub account

4. Upload your resume file in any of the supported formats (md, PDF, Word, etc.). They all will be converted to markdown using MarkItDown

5. Choose a template style (Basic, Modern, or Terminal)

6. Preview and customize the rendered content. Use the AI assistant to enhance your resume's content and formatting

7. Save to GitHub or export as needed. Your resume will be hosted on GitHub Pages automatically

## Development Notes

Built using:
- Flask for the web framework
- GitHub API for seamless integration
- OpenAI for content enhancement
- Modern development practices

The entire project was completed in 24 hours using AI pair programming, demonstrating how AI tools can be effectively integrated into the development workflow.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [MarkItDown](https://github.com/microsoft/markitdown) for document conversion
- Flask web framework
- GitHub API for seamless integration
- OpenAI for AI-powered resume enhancement
