#!/bin/bash

###############################################################################
# Video-AI Browser Extension Build Script
# 为 Chrome、Firefox 和 Edge 打包浏览器扩展
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/dist"
VERSION=$(grep '"version"' manifest.json | sed 's/.*"version": "\([^"]*\)".*/\1/')

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Video-AI Browser Extension Build Tool${NC}"
echo -e "${BLUE}Version: ${VERSION}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 创建输出目录
mkdir -p "${BUILD_DIR}"

# 清理旧文件
echo -e "${YELLOW}Cleaning old build files...${NC}"
rm -f "${BUILD_DIR}"/*.zip

# ============================================================================
# 函数：打包扩展
# ============================================================================

package_extension() {
    local format=$1
    local output_name=$2

    echo -e "${BLUE}Packaging for ${format}...${NC}"

    # 排除不需要的文件
    local exclude_flags="--exclude=dist --exclude=build.sh --exclude=.git --exclude=.gitignore --exclude=*.md"

    # 创建 ZIP 文件
    cd "${SCRIPT_DIR}"
    zip -r -q "${BUILD_DIR}/${output_name}" . ${exclude_flags}

    local file_size=$(du -h "${BUILD_DIR}/${output_name}" | cut -f1)
    echo -e "${GREEN}✓ ${output_name} (${file_size})${NC}"
}

# ============================================================================
# 打包不同浏览器版本
# ============================================================================

# Chrome 扩展
package_extension "Chrome" "video-ai-chrome-${VERSION}.zip"

# Firefox 扩展（需要 Manifest V2 版本，但现在使用 V3）
package_extension "Firefox" "video-ai-firefox-${VERSION}.zip"

# Edge 扩展
package_extension "Edge" "video-ai-edge-${VERSION}.zip"

# ============================================================================
# 生成校验和
# ============================================================================

echo ""
echo -e "${BLUE}Generating checksums...${NC}"

cd "${BUILD_DIR}"

if command -v sha256sum &> /dev/null; then
    sha256sum *.zip > checksums.txt
    echo -e "${GREEN}✓ checksums.txt created${NC}"
elif command -v shasum &> /dev/null; then
    shasum -a 256 *.zip > checksums.txt
    echo -e "${GREEN}✓ checksums.txt created${NC}"
fi

# ============================================================================
# 显示打包信息
# ============================================================================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Output directory:${NC} ${BUILD_DIR}"
echo ""
echo -e "${BLUE}Generated packages:${NC}"
ls -lh "${BUILD_DIR}"/*.zip 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo -e "${BLUE}Installation instructions:${NC}"
echo ""
echo -e "${YELLOW}Chrome/Chromium:${NC}"
echo "  1. Open chrome://extensions/"
echo "  2. Enable 'Developer mode' (top right)"
echo "  3. Click 'Load unpacked'"
echo "  4. Select the extension folder"
echo ""
echo -e "${YELLOW}Firefox:${NC}"
echo "  1. Open about:debugging#/runtime/this-firefox"
echo "  2. Click 'Load Temporary Add-on'"
echo "  3. Select manifest.json from the extension folder"
echo ""
echo -e "${YELLOW}Edge:${NC}"
echo "  1. Open edge://extensions/"
echo "  2. Enable 'Developer mode' (bottom left)"
echo "  3. Click 'Load unpacked'"
echo "  4. Select the extension folder"
echo ""

# ============================================================================
# 验证
# ============================================================================

echo -e "${BLUE}Verification:${NC}"

# 检查必要的文件
required_files=(
    "manifest.json"
    "popup.html"
    "popup.js"
    "content.js"
    "background.js"
    "options.html"
    "options.js"
    "styles/popup.css"
    "styles/content.css"
    "icons/icon16.png"
    "icons/icon48.png"
    "icons/icon128.png"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ -f "${SCRIPT_DIR}/${file}" ]; then
        echo -e "  ${GREEN}✓${NC} ${file}"
    else
        echo -e "  ${RED}✗${NC} ${file} (missing)"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -eq 0 ]; then
    echo ""
    echo -e "${GREEN}All required files present!${NC}"
else
    echo ""
    echo -e "${RED}Warning: ${missing_files} required file(s) missing!${NC}"
    exit 1
fi

echo ""
