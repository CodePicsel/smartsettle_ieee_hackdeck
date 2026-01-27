package com.example.splitexpense.network;

import com.example.splitexpense.models.SendOtpRequest;
import com.example.splitexpense.models.VerifyOtpRequest;
import com.example.splitexpense.models.VerifyOtpResponse;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface ApiService {

    @POST("/auth/request-otp")
    Call<Void>  requestOtp(@Body SendOtpRequest request);

    @POST("/auth/verify-otp")
    Call<VerifyOtpResponse> verifyOtp(@Body VerifyOtpRequest request);
}
