import useProfile from "../hooks/useProfile";

function Dashboard() {
  const { user, loading, error } = useProfile();

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Welcome, {user.name}</h2>
      <p>Phone: {user.phone}</p>
      <p>User ID: {user.id}</p>
    </div>
  );
}

export default Dashboard;
