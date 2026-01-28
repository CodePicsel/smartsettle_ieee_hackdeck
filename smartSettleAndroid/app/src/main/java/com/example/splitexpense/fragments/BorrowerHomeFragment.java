package com.example.splitexpense.fragments;

import android.os.Bundle;
import android.view.*;
import android.widget.EditText;
import android.widget.Toast;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.android.volley.Request;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.splitexpense.R;
import com.example.splitexpense.adapters.OfferAdapter;
import com.example.splitexpense.adapters.OfferClickListener;
import com.example.splitexpense.models.Offer;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class BorrowerHomeFragment extends Fragment {

    private RecyclerView recyclerView;
    private List<Offer> offerList = new ArrayList<>();

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_borrower_home, container, false);
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        recyclerView = view.findViewById(R.id.recyclerOffers);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        loadOffers();
    }

    private void loadOffers() {
        String url = "http://10.0.2.2:8000/offers/latest";

        JsonArrayRequest request = new JsonArrayRequest(Request.Method.GET, url, null,
                response -> parseOffers(response),
                error -> Toast.makeText(getContext(), "Failed to load offers", Toast.LENGTH_SHORT).show()
        );

        Volley.newRequestQueue(requireContext()).add(request);
    }

    private void parseOffers(JSONArray array) {
        try {
            offerList.clear();
            for (int i = 0; i < array.length(); i++) {
                JSONObject obj = array.getJSONObject(i);
                Offer offer = new Offer();
                offer.offerId = obj.getInt("offer_id");
                offer.lenderName = obj.getJSONObject("lender").getString("name");
                offer.amountAvailable = obj.getDouble("amount_available");
                offer.interestRate = obj.getDouble("annual_interest_rate");
                offer.durationMonths = obj.getInt("duration_months");
                offer.installmentAmount = obj.optDouble("installment_amount", 0);
                offer.periodicity = obj.optString("periodicity", "MONTHLY");
                offer.description = obj.optString("description", "");
                offerList.add(offer);
            }

            String token = requireActivity()
                    .getSharedPreferences("auth", getContext().MODE_PRIVATE)
                    .getString("token", "");

            OfferAdapter adapter = new OfferAdapter(getContext(), offerList, token, offer -> showApplyDialog(offer));
            recyclerView.setAdapter(adapter);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // -------------------------
    // Show dialog to apply for offer
    // -------------------------
    private void showApplyDialog(Offer offer) {
        View dialogView = LayoutInflater.from(getContext()).inflate(R.layout.dialog_apply_offer, null);
        EditText etAmount = dialogView.findViewById(R.id.etAmount);
        EditText etDate = dialogView.findViewById(R.id.etStartDate);

        androidx.appcompat.app.AlertDialog dialog = new androidx.appcompat.app.AlertDialog.Builder(getContext())
                .setTitle("Apply for Offer")
                .setView(dialogView)
                .setNegativeButton("Cancel", (d, which) -> d.dismiss())
                .setPositiveButton("Apply", null)
                .create();

        dialog.setOnShowListener(d -> {
            dialog.getButton(androidx.appcompat.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
                String strAmount = etAmount.getText().toString().trim();
                String strDate = etDate.getText().toString().trim();

                if (strAmount.isEmpty()) {
                    etAmount.setError("Enter amount");
                    return;
                }
                if (strDate.isEmpty()) {
                    etDate.setError("Enter start date");
                    return;
                }

                double amountRequested = Double.parseDouble(strAmount);
                applyForOffer(offer.offerId, amountRequested, strDate);
                dialog.dismiss();
            });
        });

        dialog.show();
    }

    // -------------------------
    // Apply for offer via POST
    // -------------------------
    private void applyForOffer(int offerId, double amountRequested, String startDate) {
        String url = "http://10.0.2.2:8000/offers/" + offerId + "/fund";

        JSONObject body = new JSONObject();
        try {
            body.put("amount_requested", amountRequested);
            body.put("start_date", startDate);
        } catch (Exception e) {
            e.printStackTrace();
        }

        String token = requireActivity()
                .getSharedPreferences("auth", getContext().MODE_PRIVATE)
                .getString("token", "");

        JsonObjectRequest request = new JsonObjectRequest(Request.Method.POST, url, body,
                response -> Toast.makeText(getContext(), "Applied successfully!", Toast.LENGTH_SHORT).show(),
                error -> Toast.makeText(getContext(), "Failed to apply: " + error.getMessage(), Toast.LENGTH_SHORT).show()
        ) {
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Authorization", "Bearer " + token);
                return headers;
            }
        };

        Volley.newRequestQueue(requireContext()).add(request);
    }
}
