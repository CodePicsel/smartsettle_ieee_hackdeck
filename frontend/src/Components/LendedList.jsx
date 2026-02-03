function LendedList({ offers }) {
  if (!offers || offers.length === 0) {
    return (
      <div className="bg-white rounded-lg p-4 text-black">
        No lended offers found.
      </div>
    );
  }

  return (
    <div>
      {offers.map((o) => (
        <div
          key={o.offer_id}
          className="p-2 m-2 rounded-lg hover:bg-gray-100 text-black"
        >
          <div className="flex p-2 m-2 justify-between">
            <div>
              <h3 className="text-2xl font-[poppins-sb]">
                {o.lender?.name || "You"}
              </h3>
              <p className="text-sm text-gray-600">
                {o.description}
              </p>
            </div>

            <div className="text-right">
              <p className="text-[1rem] text-gray-800">
                {new Date(o.created_at).toLocaleDateString()}
              </p>
              <p className="font-[poppins-sb]">
                ₹{o.amount_available}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default LendedList;
