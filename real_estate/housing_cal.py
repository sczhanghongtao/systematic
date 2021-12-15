import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def dcf(interest,periods):
    res = np.empty(periods)
    res[0] = 1/(1+interest)
    for i in range(1, periods):
        res[i] = res[i-1]/(1+interest)
    return res
def fcf(interest,periods):
    res = np.empty(periods)
    res[0] = 1
    for i in range(1, periods):
        res[i] = res[i-1]*(1+interest)
    return res[::-1]

class Housing:
    def __init__(self,args):
        for k, v in args.items():
            setattr(self, k, v)
    @property
    def inflation_multiplier(self):
    	return sum(fcf((1+self.inflation)**(1/12)-1,int(self.investing_years*12)))/(self.investing_years*12)
    @property
    def appreciation_multiplier(self):
        return sum(fcf((1+self.appreciation)**(1/12)-1,int(self.investing_years*12)))/(self.investing_years*12)
    @property
    def cost(self):
        return self.inflation_multiplier*(self.property_tax*self.house_price+self.hoa+self.insurance*self.house_price + self.house_price*self.repairs) - (self.house_price*self.tenant_income)*self.appreciation_multiplier
    @property
    def loan_amount(self):
        return self.house_price*(1-self.down_payment)
    @property
    def months(self):
        return self.years*12

    def loans_cal(self,monthly_payment):
        interest_array = np.zeros(self.months+1)
        principal_array = np.zeros(self.months+1)
        principal_array[0] = self.loan_amount
        for m in range(1,self.months+1):
            interest_array[m] = principal_array[m-1]*self.apr
            principal_array[m] = principal_array[m-1] - (monthly_payment - interest_array[m])
        self.interest_array = interest_array
        self.principal_array = principal_array
        
    def payment_objective_func(self,monthly_payment):
        total_loan = 0
        self.loans_cal(monthly_payment)
        total_loan =self.loan_amount+sum(self.interest_array)
        return abs(monthly_payment*self.months-total_loan)
    

    def monthly_payment_cal(self):
        res = minimize(self.payment_objective_func, 1600,method = 'Nelder-Mead')
        self.monthly_payment = res.x[0] + self.cost

    @property
    def tax_benefit(self):
        return np.dot(self.interest_array[:int(self.investing_years*12)]*self.income_tax,self.fcf_array)
    @property
    def mirr(self):
        appreciation = self.house_price*(1+self.appreciation)**(self.investing_years)

        self.fcf_array = fcf(self.stock_return,int(self.investing_years*12))
        self.dcf_array = dcf(self.financing_cost,int(self.investing_years*12))
        self.monthly_payment_cal()

        self.appreciation_amount = (appreciation*0.94 - self.principal_array[int(self.investing_years*12)])*self.fcf_array[-1]

        #positive cash flow
        if self.monthly_payment < 0:
            self.cash_flow = -self.monthly_payment*sum(self.fcf_array)
            return ((self.appreciation_amount + self.tax_benefit + self.cash_flow)/(self.house_price*self.down_payment))**(1/self.investing_years)-1
        else:
            self.cash_flow = -self.monthly_payment*sum(self.dcf_array)
            return ((self.appreciation_amount+ self.tax_benefit)/(self.house_price*self.down_payment-self.cash_flow))**(1/self.investing_years)-1


def sensitivity(obj:Housing,attr:str,lower:float,upper:float):
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
