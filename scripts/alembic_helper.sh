#!/bin/bash
# Script helper cho Alembic commands

# Màu cho output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hàm print với màu
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Lấy tham số command
COMMAND=$1
MESSAGE=$2

# Kiểm tra xem có tham số không
if [ -z "$COMMAND" ]; then
    echo "📖 Alembic Helper - Công cụ hỗ trợ migrations"
    echo ""
    echo "Cách sử dụng: ./scripts/alembic_helper.sh [COMMAND] [MESSAGE]"
    echo ""
    echo "Commands:"
    echo "  create <message>      - Tạo migration tự động"
    echo "  manual <message>      - Tạo migration trống (thủ công)"
    echo "  upgrade               - Áp dụng tất cả migrations (nâng cấp)"
    echo "  downgrade             - Hoàn tác 1 migration (giảm cấp)"
    echo "  history               - Xem lịch sử migrations"
    echo "  current               - Xem revision hiện tại"
    echo "  heads                 - Xem branch heads"
    echo ""
    echo "Ví dụ:"
    echo "  ./scripts/alembic_helper.sh create 'add user table'"
    echo "  ./scripts/alembic_helper.sh upgrade"
    exit 0
fi

# Thực hiện các command
case "$COMMAND" in
    create)
        if [ -z "$MESSAGE" ]; then
            print_warning "Cần nhập message cho migration. Ví dụ: ./scripts/alembic_helper.sh create 'add user table'"
            exit 1
        fi
        print_info "Tạo migration tự động: $MESSAGE"
        alembic revision --autogenerate -m "$MESSAGE"
        print_success "Migration được tạo!"
        ;;
    
    manual)
        if [ -z "$MESSAGE" ]; then
            print_warning "Cần nhập message cho migration. Ví dụ: ./scripts/alembic_helper.sh manual 'custom migration'"
            exit 1
        fi
        print_info "Tạo migration trống: $MESSAGE"
        alembic revision -m "$MESSAGE"
        print_success "Migration được tạo! Hãy chỉnh sửa file trong alembic/versions/"
        ;;
    
    upgrade)
        print_info "Áp dụng tất cả migrations..."
        alembic upgrade head
        print_success "Upgrade hoàn tất!"
        alembic current
        ;;
    
    downgrade)
        print_info "Hoàn tác 1 migration..."
        alembic downgrade -1
        print_success "Downgrade hoàn tất!"
        alembic current
        ;;
    
    history)
        print_info "Lịch sử migrations:"
        alembic history
        ;;
    
    current)
        print_info "Revision hiện tại:"
        alembic current
        ;;
    
    heads)
        print_info "Branch heads:"
        alembic heads
        ;;
    
    *)
        print_warning "Command không tìm thấy: $COMMAND"
        echo "Chạy './scripts/alembic_helper.sh' để xem danh sách commands"
        exit 1
        ;;
esac
