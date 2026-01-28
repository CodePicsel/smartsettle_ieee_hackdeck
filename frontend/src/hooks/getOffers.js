import { useEffect, useState } from "react";

const useOffers = (limit = 10, offset = 0) => {
  const [offers, setOffers] = useState([]);
  const [nextOffset, setNextOffset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOffers = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/offers?limit=${limit}&offset=${offset}`
        );

        if (!res.ok) {
          throw new Error("Failed to fetch offers");
        }

        const data = await res.json();

        setOffers(data.offers);          // 👈 from Postman response
        setNextOffset(data.next_offset); // 👈 pagination
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOffers();
  }, [limit, offset]);

  return { offers, nextOffset, loading, error };
};

export default useOffers;
