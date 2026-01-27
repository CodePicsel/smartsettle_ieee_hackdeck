package com.example.splitexpense.models;

public class SendOtpRequest {
    private String phone;

    public SendOtpRequest(String phone) {
        this.phone = phone;
    }

    public String getPhone() {
        return phone;
    }
}
