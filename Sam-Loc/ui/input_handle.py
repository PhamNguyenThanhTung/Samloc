"""
Xử lý input từ người dùng
"""
class InputHandler:
    @staticmethod
    def get_menu_choice(min_choice, max_choice):
        """Lấy lựa chọn từ menu"""
        while True:
            try:
                choice = int(input(f"Chọn ({min_choice}-{max_choice}): "))
                if min_choice <= choice <= max_choice:
                    return choice
                print(f"Vui lòng nhập số từ {min_choice} đến {max_choice}")
            except ValueError:
                print("Vui lòng nhập số!")

    @staticmethod
    def get_number(prompt, min_val, max_val, default=None):
        """Lấy số từ người dùng với giới hạn"""
        while True:
            try:
                if default:
                    input_str = input(f"{prompt} (mặc định: {default}): ")
                    if not input_str:
                        return default
                    value = int(input_str)
                else:
                    value = int(input(f"{prompt}: "))

                if min_val <= value <= max_val:
                    return value
                print(f"Vui lòng nhập số từ {min_val} đến {max_val}")
            except ValueError:
                print("Vui lòng nhập số hợp lệ!")

    @staticmethod
    def get_string(prompt, default=None):
        """Lấy chuỗi từ người dùng"""
        if default:
            result = input(f"{prompt} (mặc định: '{default}'): ").strip()
            return result if result else default
        return input(f"{prompt}: ").strip()

    @staticmethod
    def get_confirmation(prompt):
        """Lấy xác nhận Yes/No"""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ['y', 'yes', 'có']:
                return True
            elif response in ['n', 'no', 'không']:
                return False
            print("Vui lòng nhập 'y' hoặc 'n'")