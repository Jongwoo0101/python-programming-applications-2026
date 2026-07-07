class BankAccount:
    def __init__(self, name, number, balance):
        self.name = name
        self.number = number
        self.balance = balance

    # 입금 메서드
    def deposit(self, money):
        self.balance += money

    # 출금 메서드
    def withdraw(self, money):
        if self.balance >= money:
            self.balance -= money
        else:
            print("잔액이 부족합니다.")


class SavingsAccount(BankAccount):
    def __init__(self, name, number, balance, interest_rate):
        super().__init__(name, number, balance)
        self.interest_rate = interest_rate

    # 이자 계산
    def add_interest(self):
        self.balance += self.balance * self.interest_rate


# 객체 입력
account = SavingsAccount("홍길동", 1001, 10000, 0.05)

# 이자 지급
account.add_interest()

# 결과 출력
print(f"예금주 = {account.name}", end='  ')
print(f"저축액 = {10000} 원", end='  ')
print(f"이자율 = {account.interest_rate * 100:.1f} %")
print(f"저축예금의 잔액= {account.balance} 원")