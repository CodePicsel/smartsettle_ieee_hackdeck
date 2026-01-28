import useOffers from "../hooks/getOffers";

function AvailableLenders() {
  const { offers, loading, error } = useOffers();

  if (loading) return <p>Loading offers...</p>;
  if (error) return <p>{error}</p>;

    return  (
    <div className="flex flex-col w-full overflow-y-scroll max-h-screen">
      {offers.map((offer) => (
        <div>
             <div key={offer.offer_id} className="flex justify-between p-2 m-2  rounded-lg hover:bg-gray-100 text-black ">
                <div className="p-2 flex flex-col self-center">
                        <h3 className="font-[poppins-sb] text-2xl">{offer.lender.name}</h3>
                        <p className="font-[poppins-lt]">Amount: ₹{offer.amount_available}</p>
                        <p className="font-[poppins-lt]">Duration: {offer.duration_months} months</p>
                </div>
                    <div className="p-2 flex flex-col self-center">
                        <p className="font-[poppins-lt]">EMI: ₹{offer.installment_amount}</p>
                        <p className="font-[poppins-lt]">Interest: {offer.annual_interest_rate}%</p>
                    </div>
            </div>
            <hr className="border-4" />
        </div>
      ))}
    </div>
    // <div className="flex flex-col w-full">
    //   {offers.map((offer) => (
    //     <div key={offer.offer_id} className="flex justify-between p-2 m-2 border-2 rounded-lg bg-orange-50 text-black ">
    //         <div className="p-2 flex flex-col self-center">
    //         <h3 className="font-[poppins-sb] text-2xl">{offer.lender.name}</h3>
    //         <p className="font-[poppins-lt]">Amount: ₹{offer.amount_available}</p>
    //         <p className="font-[poppins-lt]">Duration: {offer.duration_months} months</p>
    //         </div>
    //         <div className="p-2 flex flex-col self-center">
    //         <p className="font-[poppins-lt]">EMI: ₹{offer.installment_amount}</p>
    //         <p className="font-[poppins-lt]">Interest: {offer.annual_interest_rate}%</p>
    //         </div>
    //     </div>
    //   ))}
    // </div>
  );
}

export default AvailableLenders;
