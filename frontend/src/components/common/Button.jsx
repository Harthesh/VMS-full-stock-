export default function Button({ children, variant = "primary", className = "", ...props }) {
  const classes = {
    primary: "btn-primary",
    secondary: "btn-secondary",
    danger: "btn-danger",
  };

  return (
    <button className={`${classes[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

