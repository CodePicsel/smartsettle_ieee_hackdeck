import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import AvailableLenders from "./AvailableOffers";
import Modal from "./Modal";
import CreateOffer from "./CreateOffer";

const BASE_URL = "http://localhost:8000";

function Profile() {

    const [showCreateOffer, setShowCreateOffer] = useState(false);
    
  // Redux user (supports multiple slice shapes)
  const reduxUser = useSelector(
    (state) => state.auth?.user || state.auth?.userData || null
  );

  const [user, setUser] = useState(reduxUser);
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // tabs: borrowed | lended | available
  const [activeTab, setActiveTab] = useState("lended");

  const token = sessionStorage.getItem("access_token");
  const sessionPhone = sessionStorage.getItem("phone");

  /* ---------------- FETCH USER (fallback) ---------------- */
  useEffect(() => {
    async function fetchUserFallback() {
      if (user || !token) return;

      setLoading(true);
      try {
        const res = await fetch(`${BASE_URL}/debug/users`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Failed to fetch user");

        const data = await res.json();

        if (Array.isArray(data)) {
          const found =
            data.find((u) => u.phone === sessionPhone) || data[0] || null;
          setUser(found);
        } else if (data.user) {
          setUser(data.user);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchUserFallback();
  }, [user, token, sessionPhone]);

  /* ---------------- FETCH OFFERS ---------------- */
  useEffect(() => {
    async function fetchOffers() {
      setLoading(true);
      try {
        const res = await fetch(`${BASE_URL}/offers?limit=20&offset=0`);
        if (!res.ok) throw new Error("Failed to fetch offers");

        const data = await res.json();
        setOffers(data.offers || []);
      } catch (err) {
        console.warn("Offers fetch failed:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchOffers();
  }, []);

  /* ---------------- USER OWNED OFFERS (LENDED) ---------------- */
  const userOffers = offers.filter(
    (o) =>
      o.lender?.name === user?.name ||
      o.lender?.phone === user?.phone ||
      o.lender?.phone === sessionPhone
  );

  const totalLended = userOffers.reduce(
    (sum, o) => sum + Number(o.amount_available || 0),
    0
  );

  const totalBorrowed = 0; // placeholder until loans API

  /* ---------------- STATES ---------------- */
  if (loading && !user) {
    return <div className="p-6 text-white">Loading profile...</div>;
  }

  if (!user) {
    return (
      <div className="p-6 text-white">
        <h2 className="text-xl font-semibold">No profile found</h2>
        <p className="text-gray-400">Please login to continue.</p>
      </div>
    );
  }

  /* ---------------- UI ---------------- */
  return (
    <div className="w-full text-white">
      <div className="flex">
        {/* LEFT PANEL */}
        <div className="w-1/4 bg-blue-900 p-4 border-2 border-blue-950 h-screen">
          <div className="flex items-center gap-4 border-l border-t border-gray-400 rounded-lg bg-blue-800 shadow-[5px_5px_0px_0px_rgba(0,_0,_0,_0.7)] p-5">
            <img
              src={
                user.avatar ||
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpB0DSTiS-zIom7MhFF_vzpYEn0nRzlHQaow&s"
              }
              alt="avatar"
              className="h-24 w-24 rounded-full border mb-3"
            />
            <div className="flex flex-col gap-1">
                <h2 className="text-3xl font-[poppins-sb] font-bold">{user.name}</h2>
                <p className="font-[poppins-lt] text-gray-100">
                  Phone: {user.phone || sessionPhone}
                </p>
            </div>
          </div>

          <hr className="my-4 border-gray-300" />

          <div className="space-y-4">
            <div className="bg-white text-black p-4  shadow-[5px_5px_0px_0px_rgba(0,_0,_0,_0.7)] rounded border">
              <p className="font-[poppins-lt] text-black">Total Lended</p>
              <p className="text-2xl font-bold mt-1">₹{totalLended}</p>
            </div>

            <div className="bg-white text-black p-4 shadow-[5px_5px_0px_0px_rgba(0,_0,_0,_0.7)] rounded border">
              <p className="font-[poppins-lt] text-black">Total Borrowed</p>
              <p className="text-2xl font-bold mt-1">₹{totalBorrowed}</p>
            </div>
          </div>
          {/* Create Offer Button */}
            <div className="py-4">
            {/* Profile content */}

            <button
                onClick={() => setShowCreateOffer(true)}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-white"
            >
                + Create Offer
            </button>

            {/* Modal */}
            <Modal
                isOpen={showCreateOffer}
                onClose={() => setShowCreateOffer(false)}
            >
                <CreateOffer />
            </Modal>
            </div>
        </div>

        

        {/* RIGHT PANEL */}
        <div className="flex-1">
          {/* TABS */}
          <div className="flex justify-evenly items-center mb-4 h-25 bg-blue-700 border-b-4 border-blue-800  p-3">
            {["borrowed", "lended", "available"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-2 rounded uppercase hover:text-white h-fit transition font-[poppins-sb] ${
                  activeTab === tab
                    ? "text-white"
                    : "text-gray-400"
                }`}
              >
                {tab === "available" ? "Available Lenders" : tab}
              </button>
            ))}
          </div>

          {/* TAB CONTENT */}
          <div className="space-y-4  p-2 m-2 my-4 flex flex-col max-h-screen overflow-y-scroll ">
            {/* LENDED */}
            {activeTab === "lended" &&
              (userOffers.length ? (
                userOffers.map((o) => (
                  <div
                    key={o.offer_id}
                    className="p-2 m-2  rounded-lg hover:bg-gray-100 text-black"
                  >
                    <div className="flex  p-2 m-2 justify-between">
                      <div>
                        <h3 className="text-2xl font-[poppins-sb]">
                          {o.lender?.name}
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
                ))
              ) : (
                <div className="bg-white rounded-lg p-4 text-black">
                  No lended offers found.
                </div>
              ))}

            {/* BORROWED */}
            {activeTab === "borrowed" && (
              <div className="bg-white rounded-lg p-4 text-black">
                No borrowed loans yet.
              </div>
            )}

            {/* AVAILABLE LENDERS */}
            {activeTab === "available" && (
              <div className="bg-white  rounded-lg p-4">
                <AvailableLenders />
              </div>
            )}
          </div>
        </div>
      </div>

      {error && <p className="text-red-400 mt-4">{error}</p>}
    </div>
  );
}

export default Profile;
