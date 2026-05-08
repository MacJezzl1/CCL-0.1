#!/bin/bash
# EAS Build Script for GenX Mobile
# Run: bash build-mobile.sh [platform] [profile]
# Example: bash build-mobile.sh ios production

PLATFORM=${1:-all}
PROFILE=${2:-production}
PROJECT_DIR=~/CCL_0.1/mobile

echo "=========================================="
echo "  GenX Mobile - EAS Build Script"
echo "=========================================="
echo ""

# Check if EAS CLI is installed
if ! command -v eas &> /dev/null; then
    echo "Error: EAS CLI not found. Install with:"
    echo "npm install -g eas-cli"
    exit 1
fi

# Navigate to project
cd "$PROJECT_DIR" || exit 1

# Check if logged in
echo "Checking EAS login status..."
eas whoami || {
    echo "Please login to EAS:"
    eas login
}

# Build for specified platform
echo "Building for $PLATFORM with profile: $PROFILE"
echo ""

if [ "$PLATFORM" = "ios" ]; then
    echo "Building iOS app for App Store..."
    eas build --platform ios --profile "$PROFILE" --non-interactive
elif [ "$PLATFORM" = "android" ]; then
    echo "Building Android app for Play Store..."
    eas build --platform android --profile "$PROFILE" --non-interactive
else
    echo "Building for both iOS and Android..."
    eas build --platform all --profile "$PROFILE" --non-interactive
fi

# Check build status
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  Build Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Check build status: eas build:list"
    echo "2. Submit to App Store: eas submit --platform ios"
    echo "3. Submit to Play Store: eas submit --platform android"
    echo "4. Or use: eas submit --platform all"
else
    echo ""
    echo "Build failed! Check logs above."
    exit 1
fi
