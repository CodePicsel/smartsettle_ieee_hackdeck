package com.example.splitexpense.fragments;
import static java.security.AccessController.getContext;

import android.content.Context;
import android.os.Bundle;
//import android.telecom.Call;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.fragment.app.Fragment;

import com.example.splitexpense.R;
import com.example.splitexpense.models.CreateOfferRequest;
import com.example.splitexpense.models.CreateOfferResponse;
import com.example.splitexpense.network.ApiClient;
import com.example.splitexpense.network.ApiService;

//import javax.security.auth.callback.Callback;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import retrofit2.Response;

public class LenderOfferFragment extends Fragment {

    EditText etAmountAvailable, etInterestRate, etDurationMonths,
            etInstallments, etMinBorrow, etMaxBorrow, etDescription;
    Spinner spinnerPeriodicity;
    Button btnCreateOffer;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_lender_offer, container, false);

        etAmountAvailable = view.findViewById(R.id.etAmountAvailable);
        etInterestRate = view.findViewById(R.id.etInterestRate);
        etDurationMonths = view.findViewById(R.id.etDurationMonths);
        etInstallments = view.findViewById(R.id.etInstallments);
        etMinBorrow = view.findViewById(R.id.etMinBorrow);
        etMaxBorrow = view.findViewById(R.id.etMaxBorrow);
        etDescription = view.findViewById(R.id.etDescription);
        spinnerPeriodicity = view.findViewById(R.id.spinnerPeriodicity);
        btnCreateOffer = view.findViewById(R.id.btnCreateOffer);

        setupSpinner();

        btnCreateOffer.setOnClickListener(v -> createOffer());

        return view;
    }

    private void setupSpinner() {
        String[] options = {"MONTHLY", "WEEKLY"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_dropdown_item, options);
        spinnerPeriodicity.setAdapter(adapter);
    }

    private void createOffer() {

        String token = requireActivity()
                .getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
                .getString("access_token", null);

        if (token == null) {
            Toast.makeText(getContext(), "Session expired. Login again.", Toast.LENGTH_SHORT).show();
            return;
        }

        double amountAvailable = Double.parseDouble(etAmountAvailable.getText().toString());
        double interestRate = Double.parseDouble(etInterestRate.getText().toString());
        int durationMonths = Integer.parseInt(etDurationMonths.getText().toString());
        int installments = Integer.parseInt(etInstallments.getText().toString());
        String periodicity = spinnerPeriodicity.getSelectedItem().toString();
        Double minBorrow = Double.parseDouble(etMinBorrow.getText().toString());
        Double maxBorrow = Double.parseDouble(etMaxBorrow.getText().toString());
        String description = etDescription.getText().toString();

        CreateOfferRequest request = new CreateOfferRequest(
                amountAvailable,
                interestRate,
                durationMonths,
                installments,
                periodicity,
                minBorrow,
                maxBorrow,
                description
        );

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.createOffer("Bearer " + token, request)
                .enqueue(new Callback<CreateOfferResponse>() {
                    @Override
                    public void onResponse(Call<CreateOfferResponse> call, Response<CreateOfferResponse> response) {
                        if (response.isSuccessful() && response.body() != null) {

                            int offerId = response.body().getOfferId();
                            double emi = response.body().getInstallmentAmount();

                            Toast.makeText(getContext(),
                                    "Offer Created! EMI: ₹" + emi,
                                    Toast.LENGTH_LONG).show();

                        } else {
                            Toast.makeText(getContext(),
                                    "Failed: " + response.code(),
                                    Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<CreateOfferResponse> call, Throwable t) {
                        Toast.makeText(getContext(), "Server error", Toast.LENGTH_SHORT).show();
                    }
                });
    }

}
