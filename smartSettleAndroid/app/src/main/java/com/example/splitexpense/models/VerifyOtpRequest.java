package com.example.splitexpense.models;

public class VerifyOtpRequest {
    private String phone;
    private String otp;

    public VerifyOtpRequest(String phone, String otp) {
        this.phone = phone;
        this.otp = otp;
    }

    public String getPhone() { return phone; }
    public String getOtp() { return otp; }
}
