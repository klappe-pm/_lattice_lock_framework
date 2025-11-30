#!/bin/bash
# Power Prompts API Key Setup Script
# This script helps you configure API keys for all supported cloud providers

echo "🚀 Power Prompts - API Key Configuration"
echo "========================================"
echo ""

# Function to set API key with validation
setup_api_key() {
    local service_name="$1"
    local env_var_name="$2"
    local description="$3"
    local signup_url="$4"
    
    echo "📝 Setting up $service_name"
    echo "   Description: $description"
    echo "   Signup URL: $signup_url"
    echo ""
    
    current_key="${!env_var_name}"
    if [[ -n "$current_key" ]]; then
        echo "   ✅ API key already configured for $env_var_name"
        echo "   Current key: ${current_key:0:8}...${current_key: -4}"
    else
        echo "   ❌ No API key found for $env_var_name"
        echo "   To set up:"
        echo "   1. Visit: $signup_url"
        echo "   2. Create an account and generate an API key"
        echo "   3. Add to your shell profile (.bashrc, .zshrc, etc.):"
        echo "      export $env_var_name=\"your-api-key-here\""
        echo "   4. Or set temporarily: export $env_var_name=\"your-api-key-here\""
    fi
    echo ""
    echo "----------------------------------------"
}

# Function to show current environment setup
show_current_setup() {
    echo "🔍 Current API Key Status:"
    echo "=========================="
    
    local keys=(
        "OPENAI_API_KEY:OpenAI"
        "ANTHROPIC_API_KEY:Anthropic (Claude)"
        "GOOGLE_API_KEY:Google (Gemini)"
        "XAI_API_KEY:xAI (Grok)"
        "DIAL_API_KEY:DIAL API"
        "AZURE_OPENAI_API_KEY:Azure OpenAI"
        "AWS_ACCESS_KEY_ID:AWS Bedrock"
        "AZURE_OPENAI_ENDPOINT:Azure Endpoint"
        "AWS_SECRET_ACCESS_KEY:AWS Secret"
        "AWS_REGION:AWS Region"
    )
    
    for key_info in "${keys[@]}"; do
        IFS=':' read -r var_name display_name <<< "$key_info"
        current_value="${!var_name}"
        
        if [[ -n "$current_value" ]]; then
            echo "  ✅ $display_name ($var_name): Set"
        else
            echo "  ❌ $display_name ($var_name): Not set"
        fi
    done
    echo ""
}

# Function to create a .env template
create_env_template() {
    echo "📄 Creating .env template file..."
    
    cat > .env.example << 'EOF'
# Power Prompts API Keys Configuration
# Copy this file to .env and fill in your actual API keys
# DO NOT commit .env to version control!

# OpenAI API Key (GPT-4, GPT-3.5, DALL-E, etc.)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key (Claude models)
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google API Key (Gemini models)
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-google-api-key-here

# xAI API Key (Grok models)
# Get from: https://console.x.ai/
XAI_API_KEY=your-xai-api-key-here

# DIAL API Key (Enterprise Claude access)
# Contact your DIAL provider for access
DIAL_API_KEY=your-dial-api-key-here

# Azure OpenAI Service
# Get from: https://portal.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_ENDPOINT=your-azure-endpoint-here

# AWS Bedrock (for Claude, Llama, Titan models)
# Configure via AWS CLI or set directly
AWS_ACCESS_KEY_ID=your-aws-access-key-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
AWS_REGION=us-east-1
EOF

    echo "✅ Created .env.example template"
    echo "   Copy to .env and fill in your API keys:"
    echo "   cp .env.example .env"
    echo ""
}

# Function to load .env file
load_env_file() {
    if [[ -f ".env" ]]; then
        echo "📥 Loading environment variables from .env file..."
        set -a  # automatically export all variables
        source .env
        set +a  # stop automatically exporting
        echo "✅ Environment variables loaded"
        echo ""
    else
        echo "ℹ️  No .env file found. You can create one from .env.example"
        echo ""
    fi
}

# Main execution
main() {
    echo "This script will help you configure API keys for Power Prompts."
    echo "You'll need to sign up for services and generate API keys manually."
    echo ""
    
    # Load existing .env if available
    load_env_file
    
    # Show current status
    show_current_setup
    
    echo "🔧 API Key Setup Instructions:"
    echo "=============================="
    echo ""
    
    # Setup instructions for each provider
    setup_api_key \
        "OpenAI" \
        "OPENAI_API_KEY" \
        "Access to GPT-4, GPT-3.5-turbo, DALL-E, and other OpenAI models" \
        "https://platform.openai.com/api-keys"
    
    setup_api_key \
        "Anthropic (Claude)" \
        "ANTHROPIC_API_KEY" \
        "Access to Claude models (Opus, Sonnet, Haiku)" \
        "https://console.anthropic.com/"
    
    setup_api_key \
        "Google (Gemini)" \
        "GOOGLE_API_KEY" \
        "Access to Gemini Pro, Flash, and other Google AI models" \
        "https://makersuite.google.com/app/apikey"
    
    setup_api_key \
        "xAI (Grok)" \
        "XAI_API_KEY" \
        "Access to Grok models with 2M+ context windows" \
        "https://console.x.ai/"
    
    setup_api_key \
        "Azure OpenAI" \
        "AZURE_OPENAI_API_KEY" \
        "Enterprise access to OpenAI models via Microsoft Azure" \
        "https://portal.azure.com/"
    
    echo "📝 AWS Bedrock Setup"
    echo "   Description: Access to Claude, Llama, Titan models via AWS"
    echo "   Setup: Use AWS CLI 'aws configure' or set environment variables:"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY" 
    echo "   - AWS_REGION (e.g., us-east-1)"
    echo "   Signup URL: https://aws.amazon.com/bedrock/"
    echo ""
    echo "----------------------------------------"
    
    setup_api_key \
        "DIAL API" \
        "DIAL_API_KEY" \
        "Enterprise API access to various models" \
        "Contact your DIAL API provider"
    
    # Create template
    create_env_template
    
    echo "🎯 Next Steps:"
    echo "=============="
    echo "1. Sign up for the services you want to use"
    echo "2. Generate API keys from their dashboards"
    echo "3. Copy .env.example to .env and fill in your keys"
    echo "4. Or add export statements to your shell profile"
    echo "5. Restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc)"
    echo "6. Test with: python3 list_all_models.py"
    echo ""
    echo "💡 Pro Tips:"
    echo "- Start with OpenAI (easiest to set up)"
    echo "- Anthropic Claude has excellent reasoning capabilities"
    echo "- xAI Grok has massive context windows (2M+ tokens)"
    echo "- Local models (already working) cost $0.00"
    echo ""
    echo "🔒 Security:"
    echo "- Never commit API keys to version control"
    echo "- Use environment variables or .env files"
    echo "- .env is already in .gitignore"
    echo ""
}

# Run main function
main "$@"