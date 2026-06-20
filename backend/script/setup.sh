#!/bin/bash

################################################################################
# Adaptive Learning Platform - Complete Setup Script
# This script automates the entire project initialization process
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="adaptive-learning-backend"
DB_NAME="adaptive_learning"
DB_USER="adaptive_user"
DB_PASSWORD="adaptive_password"
PYTHON_VERSION="3.12"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

ask_yes_no() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

################################################################################
# Main Setup Functions
################################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_ok=true
    
    # Check Python
    if command_exists python3; then
        local py_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found (version $py_version)"
    else
        print_error "Python 3 is not installed"
        all_ok=false
    fi
    
    # Check PostgreSQL
    if command_exists psql; then
        local pg_version=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL found (version $pg_version)"
    else
        print_error "PostgreSQL is not installed"
        print_info "Install with: sudo apt install postgresql (Ubuntu/Debian)"
        print_info "             brew install postgresql@16 (macOS)"
        all_ok=false
    fi
    
    # Check git
    if command_exists git; then
        print_success "Git found"
    else
        print_warning "Git is not installed (recommended)"
    fi
    
    # Check make
    if command_exists make; then
        print_success "Make found"
    else
        print_warning "Make is not installed (optional but recommended)"
    fi
    
    if [ "$all_ok" = false ]; then
        print_error "Some required dependencies are missing. Please install them first."
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

install_uv() {
    print_header "Installing UV Package Manager"
    
    if command_exists uv; then
        local uv_version=$(uv --version | cut -d' ' -f2)
        print_success "UV already installed (version $uv_version)"
        
        if ask_yes_no "Do you want to update UV to the latest version?"; then
            print_info "Updating UV..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.cargo/bin:$PATH"
            print_success "UV updated successfully"
        fi
    else
        print_info "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Add to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        
        # Add to shell profile
        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.bashrc"
        fi
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.zshrc"
        fi
        
        print_success "UV installed successfully"
    fi
}

create_project_structure() {
    print_header "Creating Project Structure"
    
    # Create main directories
    local dirs=(
        "app/api/v1"
        "app/core"
        "app/models"
        "app/schemas"
        "app/services"
        "alembic/versions"
        "scripts"
        "tests"
        "logs"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            touch "$dir/__init__.py" 2>/dev/null || true
            print_success "Created directory: $dir"
        fi
    done
    
    # Create __init__.py files
    touch app/__init__.py
    touch app/api/__init__.py
    touch app/api/v1/__init__.py
    
    print_success "Project structure created"
}

setup_python_environment() {
    print_header "Setting Up Python Environment"
    
    # Set Python version
    echo "$PYTHON_VERSION" > .python-version
    print_info "Set Python version to $PYTHON_VERSION"
    
    # Install dependencies
    print_info "Installing project dependencies (this may take a minute)..."
    uv sync --all-extras
    
    print_success "Python environment configured"
}

configure_database() {
    print_header "Configuring Database"
    
    # Check if PostgreSQL is running
    if ! pg_isready -q; then
        print_warning "PostgreSQL is not running"
        if ask_yes_no "Do you want to start PostgreSQL?"; then
            if command_exists systemctl; then
                sudo systemctl start postgresql
            elif command_exists brew; then
                brew services start postgresql@16
            fi
            sleep 2
        fi
    fi
    
    print_info "Database name: $DB_NAME"
    print_info "Database user: $DB_USER"
    
    if ask_yes_no "Do you want to create the database with these settings?"; then
        # Create database user (if not exists)
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || print_info "User already exists"
        
        # Create database
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || print_info "Database already exists"
        
        # Grant privileges
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null
        
        print_success "Database configured successfully"
    else
        print_warning "Skipping database creation. You'll need to create it manually."
    fi
}

setup_environment_file() {
    print_header "Setting Up Environment Variables"
    
    if [ -f .env ]; then
        if ask_yes_no ".env file already exists. Do you want to overwrite it?"; then
            rm .env
        else
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    # Generate random secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Create .env file
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Adaptive Learning Platform

# CORS Origins (comma-separated)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost:5173"]

# Environment
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000
EOF
    
    print_success ".env file created with secure random SECRET_KEY"
}

run_migrations() {
    print_header "Running Database Migrations"
    
    print_info "Initializing Alembic..."
    
    # Check if alembic is already initialized
    if [ ! -f "alembic.ini" ]; then
        uv run alembic init alembic
        print_success "Alembic initialized"
    else
        print_info "Alembic already initialized"
    fi
    
    # Update alembic.ini with database URL
    sed -i.bak "s|sqlalchemy.url = .*|sqlalchemy.url = postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME|" alembic.ini
    rm alembic.ini.bak 2>/dev/null || true
    
    print_info "Running migrations..."
    uv run alembic upgrade head
    
    print_success "Database migrations completed"
}

seed_database() {
    print_header "Seeding Database"
    
    if ask_yes_no "Do you want to seed the database with sample data?"; then
        print_info "Adding sample data..."
        uv run python scripts/seed_data.py
        print_success "Database seeded with sample data"
        
        echo ""
        print_info "Sample credentials created:"
        echo "  Username: admin"
        echo "  Password: admin123"
        echo "  Email: admin@adaptive.com"
    else
        print_info "Skipping database seeding"
    fi
}

setup_git() {
    print_header "Setting Up Git"
    
    if [ -d .git ]; then
        print_info "Git repository already initialized"
    else
        if ask_yes_no "Do you want to initialize a Git repository?"; then
            git init
            print_success "Git repository initialized"
            
            # Create .gitignore if it doesn't exist
            if [ ! -f .gitignore ]; then
                cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# UV
.uv/
uv.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db

# Alembic
alembic/versions/*.pyc
EOF
                print_success "Created .gitignore file"
            fi
        fi
    fi
}

setup_pre_commit() {
    print_header "Setting Up Pre-commit Hooks"
    
    if ask_yes_no "Do you want to install pre-commit hooks for code quality?"; then
        print_info "Installing pre-commit hooks..."
        uv run pre-commit install
        print_success "Pre-commit hooks installed"
        
        if ask_yes_no "Do you want to run pre-commit on all files now?"; then
            uv run pre-commit run --all-files || true
        fi
    else
        print_info "Skipping pre-commit setup"
    fi
}

setup_docker() {
    print_header "Docker Configuration"
    
    if command_exists docker; then
        print_success "Docker is installed"
        
        if ask_yes_no "Do you want to build the Docker image?"; then
            print_info "Building Docker image..."
            docker build -t $PROJECT_NAME:latest .
            print_success "Docker image built successfully"
            
            if ask_yes_no "Do you want to start the application with Docker Compose?"; then
                docker-compose up -d
                print_success "Application started with Docker Compose"
                print_info "API available at: http://localhost:8000"
                print_info "API docs at: http://localhost:8000/docs"
            fi
        fi
    else
        print_warning "Docker is not installed"
        print_info "To use Docker features, install Docker from: https://docs.docker.com/get-docker/"
    fi
}

run_tests() {
    print_header "Running Tests"
    
    if ask_yes_no "Do you want to run the test suite?"; then
        print_info "Running tests..."
        uv run pytest -v
        print_success "Tests completed"
    else
        print_info "Skipping tests"
    fi
}

check_system_health() {
    print_header "System Health Check"
    
    print_info "Running health checks..."
    uv run python scripts/check_health.py
}

start_development_server() {
    print_header "Starting Development Server"
    
    if ask_yes_no "Do you want to start the development server now?"; then
        print_info "Starting server on http://localhost:8000"
        print_info "API documentation: http://localhost:8000/docs"
        print_info ""
        print_info "Press Ctrl+C to stop the server"
        echo ""
        
        uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
    else
        print_info "Skipping server start"
    fi
}

print_summary() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  🎉 Setup Completed Successfully! 🎉            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📝 Quick Start Commands:${NC}"
    echo ""
    echo -e "  ${YELLOW}make run${NC}              - Start development server"
    echo -e "  ${YELLOW}make test${NC}             - Run tests"
    echo -e "  ${YELLOW}make format${NC}           - Format code"
    echo -e "  ${YELLOW}make lint${NC}             - Run linters"
    echo -e "  ${YELLOW}make migrate${NC}          - Run database migrations"
    echo -e "  ${YELLOW}make seed${NC}             - Seed database"
    echo -e "  ${YELLOW}make help${NC}             - Show all available commands"
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo ""
    echo -e "  ${BLUE}API:${NC}                  http://localhost:8000"
    echo -e "  ${BLUE}API Docs (Swagger):${NC}  http://localhost:8000/docs"
    echo -e "  ${BLUE}API Docs (ReDoc):${NC}    http://localhost:8000/redoc"
    echo ""
    echo -e "${CYAN}🔐 Sample Login Credentials:${NC}"
    echo ""
    echo -e "  ${BLUE}Username:${NC}            admin"
    echo -e "  ${BLUE}Password:${NC}            admin123"
    echo -e "  ${BLUE}Email:${NC}               admin@adaptive.com"
    echo ""
    echo -e "${CYAN}📚 Next Steps:${NC}"
    echo ""
    echo -e "  1. Review and customize the .env file"
    echo -e "  2. Read the README.md for detailed documentation"
    echo -e "  3. Start the development server with: ${YELLOW}make run${NC}"
    echo -e "  4. Visit http://localhost:8000/docs to explore the API"
    echo ""
    echo -e "${CYAN}📖 Documentation:${NC}"
    echo ""
    echo -e "  ${BLUE}Project README:${NC}      README.md"
    echo -e "  ${BLUE}API Documentation:${NC}   http://localhost:8000/docs"
    echo -e "  ${BLUE}Database Models:${NC}     app/models/"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
    echo ""
}

################################################################################
# Main Execution Flow
################################################################################

main() {
    clear
    
    echo -e "${PURPLE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        ADAPTIVE LEARNING PLATFORM - SETUP WIZARD                  ║
    ║                                                                   ║
    ║        Automated Backend Initialization & Configuration           ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo ""
    print_info "This wizard will guide you through setting up the project."
    echo ""
    
    if ! ask_yes_no "Do you want to continue with the setup?"; then
        print_info "Setup cancelled by user"
        exit 0
    fi
    
    # Run all setup steps
    check_prerequisites
    install_uv
    create_project_structure
    setup_python_environment
    setup_environment_file
    configure_database
    run_migrations
    seed_database
    setup_git
    setup_pre_commit
    setup_docker
    run_tests
    check_system_health
    
    # Print summary
    print_summary
    
    # Optionally start server
    start_development_server
}

# Run main function
main "$@"