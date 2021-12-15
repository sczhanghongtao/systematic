# Property Monthly Payment and Investing Return Calculation

## Motivation
I wrote this code to calculate monthly payment considering all the major costs, and more importantly, to understand the return from a property investment. Putting emotional value and diversification aside, in general, if the annualized return is lower than 7%, it's better to rent and invest the down payment in stock market.
## Modules
### housing_cal.py
It contains the Housing class and the method to do sensitivity analysis

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

### real_estate_return_sensitivity_analysis.ipynb
It contains my sensitivity analysis for a typical condo, townhouse, single family and duplex in California east bay.

## My Baseline Assumptions
```
args = {
# assumptions that should stay roughly unchanged from property to property
        'down_payment':0.15,
        'income_tax':0.33+0.1,
        'years':30,
        'property_tax':0.015/12,
        'insurance':0.0038/12, #85-130
        'apr':0.03/12,
        'inflation':0.02,
        'financing_cost': 0.03/12,
        'stock_return': (1+0.07)**(1/12)-1,

# assumptions that could vary a lot from property to property
        'hoa':500,
        'house_price':700000,
        'tenant_income':1/30*0.9/12,
        'repairs':0,
        'appreciation':0.02,
        'investing_years':7,
        }
```
### Varying Assumptions for Condos
condo=Housing(args)
condo.investing_years = 7
condo.house_price = 700000
condo.tenant_income = 1/23/12
condo.hoa = 500
condo.appreciation = 0.01
condo.repairs = 0 

### Varying Assumptions for Townhouse
th=Housing(args)
th.investing_years = 7
th.house_price = 950000
th.tenant_income = 1/25/12
th.hoa = 400
th.appreciation = 0.03
th.repairs = 0.005/12

### Varying Assumptions for Single Family
sfh=Housing(args)
sfh.investing_years = 10
sfh.house_price = 1000000
sfh.tenant_income = 1/25/12
sfh.hoa = 0
sfh.appreciation = 0.03
sfh.repairs = 0.01/12

## Varying Assumptions for Duplex
dp=Housing(args)
dp.investing_years = 10
dp.house_price = 1300000
dp.tenant_income = 1/20/12
dp.hoa = 0
dp.appreciation = 0.03
dp.repairs = 0.01/12

## Sensitivity Analysis Example
### changing hoa for condo
![[image/Pasted image 20211214191623.png]]
### changing house price for condo
![[image/Pasted image 20211214191656.png]]
### changing investing years for condo
![[image/Pasted image 20211214191725.png]]
### changing tenant income for duplex
![[image/Pasted image 20211214191758.png]]
