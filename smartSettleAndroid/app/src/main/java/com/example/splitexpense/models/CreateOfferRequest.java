package com.example.splitexpense.models;
public class CreateOfferRequest {

    double amount_available;
    double annual_interest_rate;
    int duration_months;
    int installments_count;
    String periodicity;
    double min_borrow_amount;
    double max_borrow_amount;
    String description;

    public CreateOfferRequest(double amount_available, double annual_interest_rate,
                              int duration_months, int installments_count,
                              String periodicity, double min_borrow_amount,
                              double max_borrow_amount, String description) {
        this.amount_available = amount_available;
        this.annual_interest_rate = annual_interest_rate;
        this.duration_months = duration_months;
        this.installments_count = installments_count;
        this.periodicity = periodicity;
        this.min_borrow_amount = min_borrow_amount;
        this.max_borrow_amount = max_borrow_amount;
        this.description = description;
    }
}
