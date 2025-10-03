import streamlit as st

def render_header():
    st.title("Amazon Competitor analysis")
    st.caption("Enter ASIN to get Product details")

def render_input():
 asin = st.text_input("Enter ASIN", placeholder="B0B1L6Z6K8")
 postal_code = st.text_input("Enter Postal Code", placeholder="M1G3E2")
 domain = st.selectbox("Select Domain", options=["com", "ca", "co.uk", "de", "fr", "it", "es","in","aed"])
 return asin.strip(), postal_code.strip(), domain


def main():
   st.set_page_config(page_title="Amazon Competitor analysis", page_icon="📚")
   render_header()
asin, postal_code, domain = render_input()



if st.button("Scarp Product") and asin:
    with st.spinner("Scraping Product details..."):
       st.write("Scraping in progress...")
       #TODO
       st.success("Product details scraped successfully!")



if __name__ == "__main__":
 main()