import { useSelector } from "react-redux";

function Profile() {
  const user = useSelector((state) => state.auth.userData);

  if (!user) return <p>Loading...</p>;

  return (
    <div>
      <h2>Profile</h2>
      <p><b>Name:</b> {user.name}</p>
      <p><b>Phone:</b> {user.phone}</p>
      <p><b>User ID:</b> {user.id}</p>
    </div>
  );
}

export default Profile;
