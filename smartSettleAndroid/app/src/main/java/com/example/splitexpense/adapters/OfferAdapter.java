package com.example.splitexpense.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.splitexpense.R;
import com.example.splitexpense.models.Offer;

import java.util.List;

public class OfferAdapter extends RecyclerView.Adapter<OfferAdapter.ViewHolder> {

    private List<Offer> offerList;
    private Context context;
    private String token;
    private OfferClickListener listener;

    public OfferAdapter(Context context, List<Offer> offerList, String token, OfferClickListener listener) {
        this.context = context;
        this.offerList = offerList;
        this.token = token;
        this.listener = listener;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvLender, tvAmount, tvInterest;
        Button btnApply;

        public ViewHolder(View view) {
            super(view);
            tvLender = view.findViewById(R.id.tvLenderName);
            tvAmount = view.findViewById(R.id.tvAmount);
            tvInterest = view.findViewById(R.id.tvInterest);
            btnApply = view.findViewById(R.id.btnApplyOffer);
        }
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_offer, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        Offer offer = offerList.get(position);
        holder.tvLender.setText("Lender: " + offer.lenderName);
        holder.tvAmount.setText("Available: ₹" + offer.amountAvailable);
        holder.tvInterest.setText("Interest: " + offer.interestRate + "%");

        holder.btnApply.setOnClickListener(v -> listener.onApplyOfferClicked(offer));
    }

    @Override
    public int getItemCount() {
        return offerList.size();
    }
}
