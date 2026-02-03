package com.example.splitexpense.fragments;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import android.content.Intent;
import android.os.Bundle;
import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.example.splitexpense.R;
import com.example.splitexpense.activities.MainActivity;
import com.example.splitexpense.models.RegisterRequest;
import com.example.splitexpense.models.VerifyOtpResponse;
import com.example.splitexpense.network.ApiClient;
import com.example.splitexpense.network.ApiService;

//import javax.security.auth.callback.Callback;


public class RegisterFragment extends Fragment {

    EditText et_name, et_address;
    Button btn_register;

    public RegisterFragment() { }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_register, container, false);

        et_name = view.findViewById(R.id.et_name);
        et_address = view.findViewById(R.id.et_address);
        btn_register = view.findViewById(R.id.btn_register);

        btn_register.setOnClickListener(v ->{

            String name = et_name.getText().toString().trim();

            if (name.isEmpty()) {
                et_name.setError("Enter your name");
                return;
            }

            Bundle args = getArguments();
            if (args == null) {
                Toast.makeText(getContext(), "Session expired. Please login again.", Toast.LENGTH_LONG).show();
                return;
            }

            String tempToken = args.getString("temp_token");
            if (tempToken == null || tempToken.isEmpty()) {
                Toast.makeText(getContext(), "Session expired, please login again", Toast.LENGTH_SHORT).show();
                return;
            }

            Toast.makeText(getContext(), "Using Temp Token: " + tempToken, Toast.LENGTH_LONG).show(); // DEBUG

            RegisterRequest request = new RegisterRequest(name);
            ApiService apiService = ApiClient.getClient().create(ApiService.class);

            apiService.registerUser("Bearer " + tempToken, request)
                    .enqueue(new Callback<VerifyOtpResponse>() {
                        @Override
                        public void onResponse(Call<VerifyOtpResponse> call, Response<VerifyOtpResponse> response) {

                            if (response.isSuccessful() && response.body() != null) {

                                String accessToken = response.body().getAccessToken();

                                Toast.makeText(getContext(), "Registration Complete!", Toast.LENGTH_SHORT).show();

                                Intent intent = new Intent(getActivity(), MainActivity.class);
                                startActivity(intent);
                                getActivity().finish();

                            } else {
                                Toast.makeText(getContext(), "Registration failed: " + response.code(), Toast.LENGTH_LONG).show();
                            }
                        }

                        @Override
                        public void onFailure(Call<VerifyOtpResponse> call, Throwable t) {
                            Toast.makeText(getContext(), "Server error: " + t.getMessage(), Toast.LENGTH_LONG).show();
                        }
                    });
        });


        return view;
    }
}
