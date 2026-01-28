package com.example.splitexpense.models;

import com.google.gson.annotations.SerializedName;

public class VerifyOtpResponse {

    @SerializedName("user_exists")
    private boolean userExists;
    @SerializedName("access_token")
    private String accessToken;
    @SerializedName("temp_token")
    private String tempToken;
    @SerializedName("user")
    private User user;   // will be null for new user

//    @SerializedName("user_id")
//    private Integer userId; // present for new user case

    public String getAccessToken() {
        return accessToken;
    }

    public User getUser() {
        return user;
    }

//    public Integer getUserId() {
//        return userId;
//    }
    public boolean isUserExists() { return userExists; }

    // Inner User class
    public static class User {

        @SerializedName("user_id")
        private int userId;

        @SerializedName("phone")
        private String phone;

        @SerializedName("name")
        private String name;

        public int getUserId() {
            return userId;
        }

        public String getPhone() {
            return phone;
        }

        public String getName() {
            return name;
        }
    }
}
