package com.example.splitexpense.models;
public class CreateOfferResponse {

    private int offer_id;
    private int lender_id;
    private double amount_available;
    private double installment_amount;
    private String status;
    private String created_at;

    public int getOfferId() { return offer_id; }
    public int getLenderId() { return lender_id; }
    public double getAmountAvailable() { return amount_available; }
    public double getInstallmentAmount() { return installment_amount; }
    public String getStatus() { return status; }
    public String getCreatedAt() { return created_at; }
}
