package com.example.splitexpense.models;

public class RegisterRequest {
    private int user_id;
    private String name;
    private String address;

    public RegisterRequest(int user_id, String name, String address) {
        this.user_id = user_id;
        this.name = name;
        this.address = address;
    }
}
