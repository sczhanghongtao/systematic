import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def dcf(interest,periods):
    """
    calculate discount rates for discounted cash flows. will be used in adjusting positive cash flows in calculating modified internal rate of return(mirr)
    :param interest: interest rate
    :param periods: number of periods
    :return: a list of discount rates for each period
    """
    res = np.empty(periods)
    res[0] = 1/(1+interest)
    for i in range(1, periods):
        res[i] = res[i-1]/(1+interest)
    return res
def fcf(interest,periods):
    """
    calculate appreciation rates for future cash flows. will be used in adjusting negative cash flows in calculating modified internal rate of return(mirr)
    :param interest: interest rate
    :param periods: number of periods
    :return: a list of appreciation rates for each period
    """
    res = np.empty(periods)
    res[0] = 1
    for i in range(1, periods):
        res[i] = res[i-1]*(1+interest)
    return res[::-1]

class Housing:
    """
    Housing encapsulates all the attributes needed to calculate monthly payment and mirr(modefied internal rate of return).

    Attributes
    __________
    down_payment: float
        down_payment relative to house_price, e.g. 0.15 means down payment is 15% of the house price
    income_tax: float
        income tax rate, e.g. 0.32
    years: int 
        mortgage years
    property_tax: float
        monthly payment to property tax, relative to house_price
    insurance: float
        monthly payment to insurance, relative to house_price
    apr: float
        monthly apr
    inflation: float
        annualized inflation
    financing_cost: float
        monthly financing cost, used to calcualte discount rate for negative cash flows in mirr
    stock_return: float
        monthly stock return, used to calculate appreciation rate for positive cash flows in mirr

    hoa: float
        monthly absolute payment to hoa
    house_price: float
        absolute house price in dollars
    tenant_income: float
        monthly tenant income, relative to house_price, e.g. it could be 1/30/12, where 30 is price to rent ratio
    repairs: float
        monthly expenditure on repairs, relative to house_price
    appreciation: float
        annualized house appreciation rate
    investing_years: int
        number of years invested in this property
    """
    def __init__(self,args):
        """
        Parameters
        __________
        args: dict
            it contains all the attributes to be initiated. below is an example - 
            args = {
            'down_payment':0.15,
            'income_tax':0.32,
            'years':30,
            'property_tax':0.015/12,
            'insurance':0.0038/12, #85-130
            'apr':0.03/12,
            'inflation':0.02,
            'financing_cost': 0.03/12,
            'stock_return': (1+0.07)**(1/12)-1,

            'hoa':500,
            'house_price':900000,
            'tenant_income':1/30*0.9/12,
            'repairs':0,
            'appreciation':0.01,
            'investing_years':7,
            }

        """
        for k, v in args.items():
            setattr(self, k, v)
    
    @property
    def inflation_multiplier(self):
        """calculate inflation multipliers to inflate cost over time"""
        return sum(fcf((1+self.inflation)**(1/12)-1,int(self.investing_years*12)))/(self.investing_years*12)

    @property
    def appreciation_multiplier(self):
        """calculate appreciation multipliers to inflate tenant_income over time"""
        return sum(fcf((1+self.appreciation)**(1/12)-1,int(self.investing_years*12)))/(self.investing_years*12)
    @property
    def cost(self):
        """cost = (property tax + hoa + insurance + repairs)*inflation_multiplier - (tenant income)*appreciation_multiplier"""
        return self.inflation_multiplier*(self.property_tax*self.house_price+self.hoa+self.insurance*self.house_price + self.house_price*self.repairs) - (self.house_price*self.tenant_income)*self.appreciation_multiplier
    @property
    def loan_amount(self):
        """calculate mortgage amount"""
        return self.house_price*(1-self.down_payment)
    @property
    def months(self):
        return self.years*12

    def loans_cal(self,monthly_payment):
        """calculate interest to be paid for each year, and outstanding loans for each year"""
        interest_array = np.zeros(self.months+1)
        principal_array = np.zeros(self.months+1)
        principal_array[0] = self.loan_amount
        for m in range(1,self.months+1):
            interest_array[m] = principal_array[m-1]*self.apr
            principal_array[m] = principal_array[m-1] - (monthly_payment - interest_array[m])
        self.interest_array = interest_array
        self.principal_array = principal_array
        
    def payment_objective_func(self,monthly_payment):
        """objective function to calculate interest and principal payment"""
        total_loan = 0
        self.loans_cal(monthly_payment)
        total_loan =self.loan_amount+sum(self.interest_array)
        return abs(monthly_payment*self.months-total_loan)
    

    def monthly_payment_cal(self):
        """calculate monthly payment = payment to interest and principal + cost"""
        res = minimize(self.payment_objective_func, 1600,method = 'Nelder-Mead')
        self.monthly_payment = res.x[0] + self.cost

    @property
    def tax_benefit(self):
        """calculate total tax benefit from deducting mortgage interest, over the whole investing years"""
        return np.dot(self.interest_array[:int(self.investing_years*12)]*self.income_tax,fcf(self.stock_return,int(self.investing_years*12)))
    @property
    def mirr(self):
        """calculate modified internal rate of return in investing this property"""
        # house appreciation over the years
        appreciation = self.house_price*(1+self.appreciation)**(self.investing_years)
        # discount & appreciation rates to be used in the following steps
        self.fcf_array = fcf(self.stock_return,int(self.investing_years*12))
        self.dcf_array = dcf(self.financing_cost,int(self.investing_years*12))
        
        # calculate monthly payment
        self.monthly_payment_cal()

        # 0.94 due to 6% transaction fee when selling the property, minus the outstanding principal, btc fcf_array[-1] is equal to 1(no appreciation at the end)
        self.appreciation_amount = (appreciation*0.94 - self.principal_array[int(self.investing_years*12)])*self.fcf_array[-1]

        #if positive cash flow, we can reinvest in stocks so there's appreciation
        if self.monthly_payment < 0:
            self.cash_flow = -self.monthly_payment*sum(self.fcf_array)
            # return annualized return on property 
            return ((self.appreciation_amount + self.tax_benefit + self.cash_flow)/(self.house_price*self.down_payment))**(1/self.investing_years)-1
        else:
        # if negative cash flow, we can discount it by our financing cost and add it in addition to our down payment
            self.cash_flow = -self.monthly_payment*sum(self.dcf_array)
            return ((self.appreciation_amount+ self.tax_benefit)/(self.house_price*self.down_payment-self.cash_flow))**(1/self.investing_years)-1


def sensitivity(obj:Housing,attr:str,lower:float,upper:float):
    """change one attribute and see how mirr changes accordingly
    :param attr: the attribute to be changed
    :param lower: start/lower limit for the changing attribute
    :param upper: end/upper limit for the changing attribute

    :return variants: the changing attribute at each step (10 steps altogether)
    :return rets: the corresponding mirr

    """
    original_value = getattr(obj,attr)
    variants = np.linspace(lower, upper, num=10)
    rets = np.empty(len(variants))
    for i in range(len(variants)):
        setattr(obj,attr,variants[i])
        rets[i] = obj.mirr
    setattr(obj,attr,original_value)
    plt.plot(variants,rets)
    plt.ylabel('Modified Internal Rate of Return')
    plt.xlabel(attr)
    return variants, rets


if __name__ == '__main__':
    args = {
    'down_payment':0.15,
    'income_tax':0.32,
	'years':30,
	'property_tax':0.015/12,
	'insurance':0.0038/12, #85-130
	'apr':0.03/12,
	'inflation':0.02,
	'financing_cost': 0.03/12,
	'stock_return': (1+0.07)**(1/12)-1,

	'hoa':500,
	'house_price':900000,
	'tenant_income':1/30*0.9/12,
	'repairs':0,
	'appreciation':0.01,
	'investing_years':7,
	}
    
    condo=Housing(args)
    print(condo.mirr)
