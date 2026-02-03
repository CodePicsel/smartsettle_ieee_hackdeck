package com.example.splitexpense.network;

import com.example.splitexpense.models.RegisterRequest;
import com.example.splitexpense.models.SendOtpRequest;
import com.example.splitexpense.models.VerifyOtpRequest;
import com.example.splitexpense.models.VerifyOtpResponse;
import com.example.splitexpense.models.CreateOfferResponse;
import com.example.splitexpense.models.CreateOfferRequest;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Header;
import retrofit2.http.POST;

public interface ApiService {

    @POST("/auth/request-otp")
    Call<Void>  requestOtp(@Body SendOtpRequest request);

    @POST("/auth/verify-otp")
    Call<VerifyOtpResponse> verifyOtp(@Body VerifyOtpRequest request);
    @POST("auth/register")
    Call<VerifyOtpResponse> registerUser(
            @Header("Authorization") String token,
            @Body RegisterRequest request
    );
    @POST("/offers")
    Call<CreateOfferResponse> createOffer(
            @Header("Authorization") String token,
            @Body CreateOfferRequest request
    );


}
